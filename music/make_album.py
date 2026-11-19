# -*- coding: utf-8 -*-
"""1시간 안팎 장편 앨범 만들기: 곡 합성 -> LP/카세트 질감 -> 크로스페이드로 연결 -> mp3 + 곡 목록/타임스탬프.

python make_album.py --minutes 60 --out out/vol01 --seed 1 [--texture lp|tape|none] [--moods ballad90,minor80,citypop80]
출력: <out>.mp3, <out>_tracks.json, <out>_description.txt (유튜브 설명용 타임스탬프 + 크레딧)
곡마다 키·템포·코드 진행·패드 여부·왼손 주법이 달라지고, 질감은 곡 단위로 걸어 앨범 전체에 일정하게 이어진다."""
import argparse, json, os, random, shutil, subprocess, tempfile
import numpy as np, soundfile as sf
import retro as R
import lp as LP, tape as TP
SR = 48000
PROGS = {
    "ballad90": [R.b90, [(0, "M7"), (9, "m7"), (2, "m7"), (7, "7"), (5, "M7"), (4, "m7"), (2, "m7"), (7, "sus")],
                 [(0, "add9"), (7, "sus"), (9, "m7"), (4, "m7"), (5, "M7"), (0, "M7"), (2, "m7"), (7, "7")]],
    "minor80": [R.m80, [(0, "m7"), (8, "M7"), (3, "M7"), (10, "7"), (0, "m7"), (5, "M7"), (7, "7"), (0, "m")]],
    "citypop80": [R.c80, [(2, "m7"), (7, "7"), (0, "M7"), (4, "m7"), (9, "m7"), (2, "m7"), (7, "7"), (0, "M7")]],
}
MINOR = {"minor80"}
BPM = {"ballad90": (60, 72), "minor80": (58, 68), "citypop80": (72, 82)}
KEYS = [55, 57, 58, 60, 62, 64, 65]     # 낮은 옥타브 기준 근음(Retro가 66 이상은 한 옥타브 내림)
A = ["밤 열한 시의", "비 그친 뒤의", "마지막 버스의", "불 꺼진 창가의", "오래된 편지의", "골목 끝의", "새벽 두 시의", "빈 방의", "여름밤의", "식어 가는 커피의",
     "멈춘 시계의", "젖은 거리의", "닫힌 가게의", "희미한 가로등의", "돌아오지 않는", "잊고 있던", "서랍 속의", "늦은 퇴근길의", "텅 빈 극장의", "겨울 저녁의"]
B = ["피아노", "노래", "안부", "기억", "멜로디", "인사", "그림자", "자장가", "고백", "여운", "마음", "산책", "엽서", "목소리", "이야기", "약속", "눈빛", "발자국", "온도", "밤"]
def titles(n, rnd):
    pairs = [(a, b) for a in A for b in B]; rnd.shuffle(pairs); return [f"{a} {b}" for a, b in pairs[:n]]
def tex(inp, out, kind, seed):
    if kind == "lp": LP.lp(inp, out, seed=seed)
    elif kind == "tape": TP.tape(inp, out, seed=seed)
    else: shutil.copy(inp, out)
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=60); ap.add_argument("--out", default="out/album"); ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--texture", default="lp", choices=["lp", "tape", "none"]); ap.add_argument("--moods", default="ballad90,minor80,citypop80")
    ap.add_argument("--pad", type=float, default=.5, help="곡에 약한 패드를 얹을 확률 (0~1)"); ap.add_argument("--xfade", type=float, default=6.0)
    a = ap.parse_args(); rnd = random.Random(a.seed); moods = a.moods.split(",")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); tmp = tempfile.mkdtemp(prefix="album_"); cwd = os.getcwd(); os.chdir(tmp)
    X = int(a.xfade * SR); tracks = []; tail = None; pos = 0.0; last_mood = None; last_key = None
    outwav = os.path.join(cwd, a.out + ".wav"); w = sf.SoundFile(outwav, "w", SR, 2, subtype="PCM_16")
    names = titles(200, rnd); i = 0
    while pos < a.minutes * 60:
        i += 1
        mood = rnd.choice([m for m in moods if m != last_mood] or moods); last_mood = mood
        key = rnd.choice([k for k in KEYS if k != last_key]); last_key = key
        prog = rnd.choice(PROGS[mood]); bpm = rnd.randint(*BPM[mood]); seed = rnd.randint(1, 10 ** 6)
        pad = round(rnd.uniform(.08, .14), 2) if rnd.random() < a.pad else 0.0; lh = rnd.choice(["arp", "block"]) if mood != "citypop80" else "arp"
        nm = f"t{i:02d}"
        R.comp(nm, key, mood in MINOR, prog, bpm, seed, pad_vol=pad, lh=lh, swing=1 if mood == "citypop80" else 0)
        tex(f"{nm}.wav", f"{nm}_x.wav", a.texture, seed)
        d, _ = sf.read(f"{nm}_x.wav", dtype="float32"); d = d / max(1e-6, np.sqrt((d ** 2).mean())) * .12   # 곡마다 비슷한 음량
        for f in (f"{nm}.wav", f"{nm}_x.wav", f"{nm}_p.wav"):
            try: os.remove(f)
            except OSError: pass
        start = 0.0 if tail is None else pos - a.xfade
        if tail is not None:                       # 앞 곡의 마지막 X초와 이번 곡의 첫 X초를 겹침
            n = min(X, len(d)); fo = np.linspace(1, 0, n)[:, None] ** .7; fi = np.linspace(0, 1, n)[:, None] ** .7
            w.write(np.clip(tail[:n] * fo + d[:n] * fi, -1, 1)); body = d[n:]
        else:
            body = d
        if len(body) > X:
            w.write(np.clip(body[:-X], -1, 1)); tail = body[-X:]
        else:
            tail = body
        tracks.append(dict(i=i, title=names[i - 1], start=round(start, 1), mood=mood, key=key, bpm=bpm, pad=pad > 0, lh=lh))
        pos = start + len(d) / SR
    if tail is not None:
        w.write(np.clip(tail, -1, 1))
    w.close(); os.chdir(cwd); shutil.rmtree(tmp, ignore_errors=True)
    # 마지막으로 전체 음량을 맞춰 mp3 로 (ffmpeg loudnorm)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", outwav, "-af", "loudnorm=I=-18:TP=-2:LRA=9", "-b:a", "192k", a.out + ".mp3"], check=True)
    os.remove(outwav)
    json.dump(tracks, open(a.out + "_tracks.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    def ts(s): s = int(s); return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60:02d}:{s % 60:02d}"
    desc = "\n".join(f"{ts(t['start'])} {t['title']}" for t in tracks) + "\n\nPiano samples: Salamander Grand Piano by Alexander Holm (CC BY 3.0)\n합성 음악(AI·코드 생성)입니다.\n"
    open(a.out + "_description.txt", "w", encoding="utf-8").write(desc)
    print(f"완료: {len(tracks)}곡 약 {pos / 60:.1f}분 -> {a.out}.mp3")
if __name__ == "__main__":
    main()
