# -*- coding: utf-8 -*-
"""따뜻한 위로(warm) + 몽환 뉴에이지(dream) 곡을 키·템포·코드 진행·질감을 바꿔 여러 곡 만들고 크로스페이드로 이어 붙인다.
python album.py --tracks 8 --out album_preview"""
import argparse, json, random, numpy as np, soundfile as sf
import retro as R
SR = 48000
WARM = [
    [(0, "M"), (7, "M"), (9, "m7"), (5, "M"), (0, "M"), (7, "M"), (5, "M7"), (7, "sus")],
    [(0, "M7"), (4, "m7"), (5, "M7"), (7, "sus"), (0, "M7"), (9, "m7"), (5, "M7"), (7, "7")],
    [(0, "add9"), (9, "m7"), (5, "add9"), (7, "sus"), (0, "add9"), (4, "m7"), (5, "M7"), (0, "add9")],
]
DREAM = [
    [(0, "add9"), (7, "add9"), (5, "M7"), (0, "add9"), (9, "m7"), (5, "M7"), (7, "sus"), (0, "add9")],
    [(0, "add9"), (5, "M7"), (9, "m7"), (7, "sus"), (0, "add9"), (5, "M7"), (9, "m7"), (7, "sus")],
    [(0, "M7"), (2, "m7"), (5, "M7"), (0, "add9"), (9, "m7"), (7, "sus"), (5, "M7"), (0, "add9")],
]
KEYS = [50, 52, 53, 55, 57, 59, 60, 62]
def plan(n, seed):
    rnd = random.Random(seed); out = []; last_key = None
    for i in range(n):
        kind = "warm" if i % 2 == 0 else "dream"
        key = rnd.choice([k for k in KEYS if k != last_key]); last_key = key
        prog = rnd.choice(WARM if kind == "warm" else DREAM)
        bpm = rnd.randint(64, 70) if kind == "warm" else rnd.randint(52, 58)
        out.append(dict(kind=kind, key=key, prog=prog, bpm=bpm, seed=rnd.randint(1, 10**6), pad=0 if kind == "warm" else round(rnd.uniform(.1, .17), 2),
                        lh="arp"))
    return out
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tracks", type=int, default=8); ap.add_argument("--out", default="album"); ap.add_argument("--seed", type=int, default=100)
    a = ap.parse_args(); tl = []; mix = None; pos = 0.0; X = 6.0
    for i, t in enumerate(plan(a.tracks, a.seed), 1):
        nm = f"{a.out}_t{i:02d}"
        R.comp(nm, t["key"], False, t["prog"], t["bpm"], t["seed"], pad_vol=t["pad"], lh=t["lh"])
        d, _ = sf.read(f"{nm}.wav", dtype="float32"); d = d / max(1e-6, np.sqrt((d ** 2).mean())) * .12   # 곡마다 비슷한 음량
        start = 0 if mix is None else int(max(0, pos - X) * SR)
        if mix is None: mix = np.zeros((0, 2), np.float32)
        need = start + len(d)
        if need > len(mix): mix = np.vstack([mix, np.zeros((need - len(mix), 2), np.float32)])
        mix[start:start + len(d)] += d; tl.append(dict(i=i, start=round(start / SR, 1), **{k: t[k] for k in ("kind", "key", "bpm")}))
        pos = start / SR + len(d) / SR
    mix = mix / np.abs(mix).max() * .85; sf.write(f"{a.out}.wav", mix, SR)
    json.dump(tl, open(f"{a.out}.json", "w"), ensure_ascii=False, indent=1); print("total", round(len(mix) / SR / 60, 1), "min")
if __name__ == "__main__":
    main()
