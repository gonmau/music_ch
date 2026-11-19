# -*- coding: utf-8 -*-
import random, numpy as np, soundfile as sf, pretty_midi as pm
from scipy import signal
import pianosynth as PS
SR = 48000
PENT = [0, 2, 4, 7, 9]
def deg_to_pitch(key, d):            # d: 펜타토닉 도수(정수, 0=key). 5개마다 한 옥타브
    return key + PENT[d % 5] + 12 * (d // 5)
def make_motif(rnd):
    """아치 모양 윤곽의 4~5음 모티프: (도수 변화, 길이[박])"""
    shape = rnd.choice([[0, 1, 2, 1], [0, 2, 1, 0], [0, 1, 0, -1, 0], [2, 1, 0, 1], [0, 3, 2, 1]])
    lens = rnd.choice([[2, 1, 2, 3], [3, 1, 2, 2], [2, 2, 1, 3], [1, 1, 2, 4], [2, 1, 1, 2, 3]])
    n = min(len(shape), len(lens))
    return shape[:n], lens[:n]
def develop(shape, lens, kind, rnd):
    if kind == "same": return shape, lens
    if kind == "up": return [s + 1 for s in shape], lens
    if kind == "down": return [s - 1 for s in shape], lens
    if kind == "inv": return [-s for s in shape], lens
    if kind == "aug": return shape, [l * 1.5 for l in lens]
    if kind == "tail": return shape[:-1] + [shape[-1] + rnd.choice([-2, 2])], lens   # 끝만 바꿈
    return shape, lens
def pad_layer(chords, bar_len, total, vol, seed):
    n = int(total * SR); out = np.zeros((n, 2), np.float32); t = np.arange(n) / SR; rnd = np.random.RandomState(seed)
    for i, notes in enumerate(chords):
        t0 = i * bar_len; a = int(max(0, t0 - 3) * SR); b = int(min(total, t0 + bar_len + 3) * SR); tt = t[a:b]
        up = np.clip((tt - (t0 - 3)) / 3.5, 0, 1); dn = np.clip(((t0 + bar_len + 3) - tt) / 3.5, 0, 1)
        env = (np.sin(up * np.pi / 2) ** 2) * (np.sin(dn * np.pi / 2) ** 2)
        for nt in notes:
            f = 440 * 2 ** ((nt - 69) / 12)
            for det, pan in ((-0.8, 0.3), (0.0, 0.5), (0.9, 0.7)):
                ff = f * 2 ** (det / 1200); lfo = 1 + 0.02 * np.sin(2 * np.pi * (0.06 + 0.03 * rnd.rand()) * tt + rnd.rand() * 6)
                s = (np.sin(2 * np.pi * ff * tt) + 0.25 * np.sin(2 * np.pi * 2 * ff * tt)) * env * lfo
                out[a:b, 0] += (s * (1 - pan)).astype(np.float32); out[a:b, 1] += (s * pan).astype(np.float32)
    return out / max(1e-6, np.abs(out).max()) * vol
def rain(total, seed, density=1.0):
    rnd = np.random.RandomState(seed); n = int(total * SR)
    w = rnd.randn(n, 2).astype(np.float32)
    sos = signal.butter(4, [1500, 9000], "bandpass", fs=SR, output="sos"); body = signal.sosfilt(sos, w, axis=0)
    t = np.arange(n) / SR; am = 1 + 0.18 * np.sin(2 * np.pi * 0.05 * t + 1) + 0.1 * np.sin(2 * np.pi * 0.13 * t)
    body *= am[:, None].astype(np.float32); body /= np.abs(body).max(); body *= 0.35
    drops = np.zeros((n, 2), np.float32)
    for _ in range(int(total * 40 * density)):          # 물방울: 짧고 높은 감쇠음
        p = rnd.randint(0, n - 4000); f = rnd.uniform(1800, 4500); L = 1800
        env = np.exp(-np.arange(L) / (SR * 0.006)); s = np.sin(2 * np.pi * f * np.arange(L) / SR) * env * rnd.uniform(0.03, 0.12)
        pan = rnd.rand(); drops[p:p + L, 0] += s * (1 - pan); drops[p:p + L, 1] += s * pan
    low = signal.sosfilt(signal.butter(2, 400, "lowpass", fs=SR, output="sos"), rnd.randn(n, 2).astype(np.float32), axis=0) * 0.05  # 먼 빗소리 저역
    return body + drops + low
def stream(total, seed):
    rnd = np.random.RandomState(seed); n = int(total * SR); t = np.arange(n) / SR
    outs = []
    for lo, hi, g in ((300, 1200, .6), (800, 3000, .45), (2000, 6000, .25)):
        w = rnd.randn(n, 2).astype(np.float32); y = signal.sosfilt(signal.butter(3, [lo, hi], "bandpass", fs=SR, output="sos"), w, axis=0)
        mod = 1 + 0.35 * np.sin(2 * np.pi * rnd.uniform(.15, .5) * t + rnd.rand() * 6) + 0.2 * np.sin(2 * np.pi * rnd.uniform(.7, 1.6) * t)
        outs.append(y * mod[:, None].astype(np.float32) * g)
    o = sum(outs); return o / np.abs(o).max() * 0.35
def compose(name, key, prog, bpm, seed, nature=None, nat_vol=0.5, pad_vol=0.0, total_chords=16, bars_each=2):
    rnd = random.Random(seed); m = pm.PrettyMIDI(initial_tempo=bpm); p = pm.Instrument(0)
    beat = 60 / bpm; blen = bars_each * 4 * beat; t = 0.0; chords = []
    motifA = make_motif(rnd); motifB = make_motif(rnd)
    plan = ["same", "up", "tail", "down", "inv", "same", "aug", "tail"]      # 모티프 변화 순서
    cur = 7
    for ci in range(total_chords):
        off, kind = prog[ci % len(prog)]
        iv = {"M7": [0, 4, 7, 11], "m7": [0, 3, 7, 10], "sus": [0, 5, 7, 10], "M": [0, 4, 7], "m9": [0, 3, 7, 10, 14], "add9": [0, 4, 7, 14]}[kind]
        root = key + off; chords.append([root - 12 + i for i in iv[:3]])
        p.notes.append(pm.Note(velocity=rnd.randint(36, 44), pitch=root - 24, start=t, end=t + blen * 1.05))
        if ci % 2 == 0:
            p.notes.append(pm.Note(velocity=rnd.randint(28, 36), pitch=root - 12 + 7, start=t + 0.3, end=t + blen))
        style = ci % 4                                  # 질감 변화: 펼친 코드 / 블록 / 높은 아르페지오 / 비움
        if style in (0, 2):
            for k, nt in enumerate([root + i for i in iv]):
                p.notes.append(pm.Note(velocity=rnd.randint(30, 40), pitch=nt, start=t + 0.5 + k * 0.30, end=t + blen * 0.9))
        elif style == 1:
            for nt in [root + i for i in iv[:3]]:
                p.notes.append(pm.Note(velocity=rnd.randint(30, 38), pitch=nt + 12, start=t + 0.4 + rnd.random() * 0.05, end=t + blen * 0.8))
        # 멜로디: 모티프를 두 번째 코드마다 이어서 변주. 모티프 사이엔 긴 쉼
        if style != 3 or ci % 8 == 3:
            base = motifA if (ci // 4) % 2 == 0 else motifB
            shape, lens = develop(*base, plan[ci % len(plan)], rnd)
            d = cur + rnd.choice([-1, 0, 0, 1])
            d = max(5, min(12, d)); pos = beat * rnd.choice([1.5, 2, 3])
            for s, l in zip(shape, lens):
                dd = max(4, min(13, d + s)); pitch = deg_to_pitch(key + 12, dd - 5)
                pitch = min(pitch, key + 31)
                vel = int(46 + 6 * (1 if l >= 2 else 0) + rnd.randint(-3, 3))
                st = t + pos + rnd.uniform(-0.03, 0.05)
                if st + l * beat < t + blen + beat:
                    p.notes.append(pm.Note(velocity=vel, pitch=int(pitch), start=st, end=st + l * beat * 1.2))
                pos += l * beat
            cur = max(5, min(12, d + shape[-1]))
        t += blen
    p.control_changes += [pm.ControlChange(64, 127, 0.0)]
    tt = 0.0
    while tt < t:
        p.control_changes += [pm.ControlChange(64, 0, tt + blen - 0.35), pm.ControlChange(64, 127, tt + blen - 0.1)]; tt += blen
    m.instruments.append(p); m.write(f"{name}.mid")
    PS.render(f"{name}.mid", f"{name}_p.wav", tail=6.0)
    pv, _ = sf.read(f"{name}_p.wav", dtype="float32"); total = len(pv) / SR
    # 피아노에 리버브(합성 임펄스) 먼저
    ir_n = int(2.8 * SR); ir = np.random.RandomState(1).randn(ir_n) * np.exp(-np.arange(ir_n) / (SR * 0.9)); ir = signal.sosfilt(signal.butter(2, 5000, "lowpass", fs=SR, output="sos"), ir)
    ir[0] = 0; wet = np.stack([signal.fftconvolve(pv[:, c], ir)[:len(pv)] for c in (0, 1)], 1).astype(np.float32)
    wet /= max(1e-6, np.abs(wet).max()); mix = pv / np.abs(pv).max() * 0.8 + wet * 0.22
    if pad_vol:
        pd = pad_layer(chords, blen, total, pad_vol, seed); mix[:len(pd)] += pd[:len(mix)]
    if nature:
        nt = (rain if nature == "rain" else stream)(total, seed); k_=min(len(mix),len(nt)); mix[:k_] += nt[:k_] * nat_vol
    fi, fo = int(4 * SR), int(8 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)[:, None]; mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
    mix = mix / np.abs(mix).max() * 0.85; sf.write(f"{name}.wav", mix, SR); print(name, round(total, 1), "s")
if __name__ == "__main__":
    C = 60
    compose("n_rain_piano", C, [(0, "M7"), (9, "m7"), (5, "M7"), (7, "sus")], 50, 11, "rain", 0.55)
    compose("n_stream_pad", C + 2, [(0, "m9"), (8, "M7"), (3, "M"), (10, "M")], 52, 21, "stream", 0.5, pad_vol=0.14)
    compose("n_rain_dawn", C + 9, [(0, "M7"), (7, "add9"), (2, "m7"), (5, "M7")], 50, 31, "rain", 0.4, pad_vol=0.12)
