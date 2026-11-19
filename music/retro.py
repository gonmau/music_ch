# -*- coding: utf-8 -*-
import random, numpy as np, soundfile as sf, pretty_midi as pm
from scipy import signal
import pianosynth as PS
from calm2 import pad_layer, rain, stream, SR
MAJ = [0, 2, 4, 5, 7, 9, 11]; MIN = [0, 2, 3, 5, 7, 8, 10]
CH = {"M7": [0, 4, 7, 11], "m7": [0, 3, 7, 10], "7": [0, 4, 7, 10], "M": [0, 4, 7], "m": [0, 3, 7], "sus": [0, 5, 7, 10], "m7b5": [0, 3, 6, 10], "add9": [0, 4, 7, 14]}
def comp(name, key, minor, bars, bpm, seed, nature=None, nat_vol=.4, pad_vol=0.0, swing=0.0, lh="arp"):
    """bars: [(근음 반음오프셋, 종류), ...] 한 마디에 코드 하나. 구조 A-A'-B-A-끝"""
    rnd = random.Random(seed); sc = MIN if minor else MAJ
    kb = key if key < 66 else key - 12
    m = pm.PrettyMIDI(initial_tempo=bpm); p = pm.Instrument(0); beat = 60 / bpm; bl = 4 * beat
    def deg(d, base):                      # 스케일 도수 -> 피치 (base: 기준 옥타브의 key)
        return base + sc[d % 7] + 12 * (d // 7)
    def chord_degs(off, kind):             # 코드톤에 해당하는 스케일 도수들
        tones = [(off + i) % 12 for i in CH[kind]]; return [d for d in range(0, 14) if sc[d % 7] in tones or (sc[d % 7] % 12) in tones]
    # 모티프 2개 (도수 이동, 박 길이). 합이 8박(2마디)
    def motif():
        sh = rnd.choice([[0, 1, 2, 1, 0], [2, 1, 0, 1, 2], [0, 2, 1, 3, 2], [0, 1, 0, -1, 0], [2, 3, 2, 1, 0]])
        ln = rnd.choice([[1, 1, 2, 1, 3], [1.5, .5, 2, 1, 3], [2, 1, 1, 1, 3], [1, 1, 1, 1, 4]])
        return sh, ln
    MA, MB = motif(), motif()
    form = ["A"] * 8 + ["A2"] * 8 + ["B"] * 8 + ["A"] * 8 + ["E"] * 8
    t = 0.0; chords = []; cur = 7 + 2
    for bi, sec in enumerate(form):
        off, kind = bars[bi % len(bars)]; root = key + off
        iv = CH[kind]; chords.append([root - 12 + i for i in iv[:3]])
        # 왼손
        low = root - 24
        if lh == "arp":
            seq = [low, low + 7, low + 12, root - 12 + iv[1], low + 12 + 7, root - 12 + iv[1]]
            for k, n_ in enumerate([seq[0], seq[1], seq[2], seq[3], seq[2], seq[1], seq[2], seq[3]]):
                sw = (beat / 6 if (swing and k % 2) else 0)
                p.notes.append(pm.Note(velocity=int(36 + 6 * (k % 4 == 0) + rnd.randint(-2, 2)), pitch=int(n_), start=t + k * beat / 2 + sw, end=t + (k + 1.6) * beat / 2))
        else:                               # 블록: 저음 + 위쪽 화음을 박마다
            p.notes.append(pm.Note(velocity=40, pitch=low, start=t, end=t + bl))
            for k in (0, 2):
                for n_ in [root - 12 + i for i in iv[:3]]:
                    p.notes.append(pm.Note(velocity=int(34 + rnd.randint(-2, 2)), pitch=int(n_), start=t + k * beat + .02 * rnd.random(), end=t + (k + 1.9) * beat))
        # 멜로디: 2마디 프레이즈의 첫 마디에서 모티프 연주, 끝은 코드톤으로
        if sec != "E" or bi % 2 == 0:
            if bi % 2 == 0:
                base = MA if sec in ("A", "A2") else MB
                shape, lens = base
                if sec == "A2": shape = [s_ + (1 if i_ >= 3 else 0) for i_, s_ in enumerate(shape)]
                if sec == "B": shape = [s_ + 2 for s_ in shape]
                d0 = {"A": 9, "A2": 9, "B": 11, "E": 8}[sec] + rnd.choice([-1, 0, 0, 1])
                pos = 0.0; ph = []
                for s_, l in zip(shape, lens):
                    ph.append((d0 + s_, pos, l)); pos += l
                # 끝 음을 코드톤으로
                cds = chord_degs(off, kind); dl, pl, ll = ph[-1]
                dl = min([c for c in cds if c + 7 >= 7] and [c + 7 for c in cds] or [dl], key=lambda x: abs(x - dl)); ph[-1] = (dl, pl, ll)
                for d_, ps, l in ph:
                    if ps >= 4 and bi % 2 == 0 and ps >= 4: pass
                    vel = int({"A": 54, "A2": 58, "B": 62, "E": 46}[sec] + rnd.randint(-3, 3))
                    st = t + ps * beat + rnd.uniform(-.02, .04)
                    p.notes.append(pm.Note(velocity=vel, pitch=int(min(deg(d_, kb), 84) if deg(d_, kb) <= 84 else deg(d_, kb) - 12), start=st, end=st + l * beat * 1.15))
        t += bl
    p.control_changes += [pm.ControlChange(64, 127, 0)]
    tt = 0.0
    while tt < t:
        p.control_changes += [pm.ControlChange(64, 0, tt + bl - .3), pm.ControlChange(64, 127, tt + bl - .08)]; tt += bl
    m.instruments.append(p); m.write(f"{name}.mid")
    PS.render(f"{name}.mid", f"{name}_p.wav", tail=6.0)
    pv, _ = sf.read(f"{name}_p.wav", dtype="float32"); total = len(pv) / SR
    ir_n = int(2.6 * SR); ir = np.random.RandomState(2).randn(ir_n) * np.exp(-np.arange(ir_n) / (SR * .8)); ir = signal.sosfilt(signal.butter(2, 5500, "lowpass", fs=SR, output="sos"), ir); ir[0] = 0
    wet = np.stack([signal.fftconvolve(pv[:, c], ir)[:len(pv)] for c in (0, 1)], 1).astype(np.float32); wet /= max(1e-6, np.abs(wet).max())
    mix = pv / np.abs(pv).max() * .8 + wet * .2
    if pad_vol:
        pd = pad_layer(chords, bl, total, pad_vol, seed); k_ = min(len(mix), len(pd)); mix[:k_] += pd[:k_]
    if nature:
        nt = (rain if nature == "rain" else stream)(total, seed); k_ = min(len(mix), len(nt)); mix[:k_] += nt[:k_] * nat_vol
    fi, fo = int(3 * SR), int(8 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]; mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
    mix = mix / np.abs(mix).max() * .85; sf.write(f"{name}.wav", mix, SR); print(name, round(total, 1), "s")
C = 60
# 90년대 서정 발라드 (C): F M7 - G - Em7 - Am7 | Dm7 - G - CM7 - Am7  (IV V iii vi / ii V I vi)
b90 = [(5, "M7"), (7, "sus"), (4, "m7"), (9, "m7"), (2, "m7"), (7, "7"), (0, "M7"), (9, "m7")]
# 80년대 시티팝 (D♭ 대신 Eb): ii-V-I-vi 재즈 진행
c80 = [(2, "m7"), (7, "7"), (0, "M7"), (9, "m7"), (5, "M7"), (4, "m7"), (2, "m7"), (7, "sus")]
# 80년대 감성 단조 발라드 (Am)
m80 = [(0, "m7"), (5, "M7"), (10, "7"), (3, "M7"), (8, "M7"), (2, "m7b5"), (7, "7"), (0, "m")]
if __name__ == "__main__":
    comp("r90_ballad_rain", C, False, b90, 62, 3, "rain", .32)
    comp("r80_citypop_stream", C + 3, False, c80, 74, 5, "stream", .3, swing=1, pad_vol=.08)
    comp("r80_minor_pad_rain", C + 9, True, m80, 60, 8, "rain", .35, pad_vol=.12, lh="block")
