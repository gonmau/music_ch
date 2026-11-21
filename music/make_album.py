# -*- coding: utf-8 -*-
"""1시간 안팎 장편 앨범 만들기: 곡 합성 -> LP/카세트 질감 -> 크로스페이드로 연결 -> mp3 + 곡 목록/타임스탬프.

python make_album.py --minutes 60 --out out/vol01 --seed 1 [--texture lp|tape|none] [--moods ballad90,minor80,citypop80]
출력: <out>.mp3, <out>_tracks.json, <out>_description.txt (유튜브 설명용 타임스탬프 + 크레딧)
곡마다 키·템포·코드 진행·패드 여부·왼손 주법이 달라지고, 질감은 곡 단위로 걸어 앨범 전체에 일정하게 이어진다."""
import argparse, json, os, random, shutil, subprocess, tempfile
import numpy as np, soundfile as sf
import retro as R
import lp as LP, tape as TP, scenes as SC
SR = 48000
PROGS = {
    "ballad90": [R.b90, [(0, "M7"), (9, "m7"), (2, "m7"), (7, "7"), (5, "M7"), (4, "m7"), (2, "m7"), (7, "sus")],
                 [(0, "add9"), (7, "sus"), (9, "m7"), (4, "m7"), (5, "M7"), (0, "M7"), (2, "m7"), (7, "7")]],
    "minor80": [R.m80, [(0, "m7"), (8, "M7"), (3, "M7"), (10, "7"), (0, "m7"), (5, "M7"), (7, "7"), (0, "m")]],
    "citypop80": [R.c80, [(2, "m7"), (7, "7"), (0, "M7"), (4, "m7"), (9, "m7"), (2, "m7"), (7, "7"), (0, "M7")]],
    "newage": [[(0, "add9"), (5, "M7"), (9, "m7"), (7, "sus"), (0, "add9"), (5, "M7"), (2, "m7"), (7, "sus")],
               [(0, "M7"), (4, "m7"), (9, "m7"), (5, "M7"), (0, "add9"), (7, "sus"), (5, "M7"), (7, "sus")]],
}
ENERGY = {"ballad90": 0, "minor80": -4, "citypop80": 10, "newage": -8}      # 곡 순서(잔잔한 곡부터)를 정하는 기준: bpm + 분위기 보정
INTRO = {"ballad90": "90년대 라디오에서 흘러나오던 서정 발라드 감성", "minor80": "80년대 단조 발라드 특유의 쓸쓸하고 깊은 여운", "citypop80": "80년대 시티팝의 도시적이고 가벼운 스윙감", "newage": "맑고 잔잔하게 흐르는 서정 피아노"}
HEAD = {"ballad90": ("밤, 혼자 듣는", "90년대 피아노 발라드"), "minor80": ("비 오는 밤에 듣는", "80년대 피아노 발라드"), "citypop80": ("퇴근길 드라이브", "80년대 시티팝 피아노"), "newage": ("고요한 밤의", "서정 피아노 연주곡")}
MIXED = ("밤, 혼자 듣는", "80~90년대 피아노 발라드")
HEAD_EN = {"ballad90": "Late Night 90s Piano Ballads", "minor80": "Rainy Night 80s Piano Ballads", "citypop80": "Night Drive 80s City Pop Piano", "newage": "Quiet Night Lyrical Piano"}
MIXED_EN = "Late Night 80s & 90s Piano Ballads"
INTRO_EN = {"ballad90": "the lyrical ballads once heard on 90s radio", "minor80": "the lonely, lingering mood of 80s minor-key ballads", "citypop80": "the light, urban swing of 80s city pop", "newage": "gently flowing lyrical piano"}
TAGS = ["80년대", "90년대", "추억의 발라드", "피아노 발라드", "피아노 연주곡", "레트로", "올드팝", "LP", "카세트", "노스탤지어", "80s", "90s", "piano ballad", "retro", "instrumental", "80s ballad", "90s ballad", "korean ballad", "nostalgic piano", "vinyl", "1980s music", "1990s music"]
MINOR = {"minor80"}
BPM = {"ballad90": (60, 72), "minor80": (58, 68), "citypop80": (72, 82), "newage": (52, 62)}
KEYS = [55, 57, 58, 60, 62, 64, 65]     # 낮은 옥타브 기준 근음(Retro가 66 이상은 한 옥타브 내림)
A = ["밤 열한 시의", "비 그친 뒤의", "마지막 버스의", "불 꺼진 창가의", "오래된 편지의", "골목 끝의", "새벽 두 시의", "빈 방의", "여름밤의", "식어 가는 커피의",
     "멈춘 시계의", "젖은 거리의", "닫힌 가게의", "희미한 가로등의", "돌아오지 않는", "잊고 있던", "서랍 속의", "늦은 퇴근길의", "텅 빈 극장의", "겨울 저녁의"]
B = ["피아노", "노래", "안부", "기억", "멜로디", "인사", "그림자", "고백", "여운", "마음", "산책", "엽서", "목소리", "이야기", "약속", "눈빛", "발자국", "온도", "밤"]
def titles(n, rnd):
    pairs = [(a, b) for a in A for b in B]; rnd.shuffle(pairs); return [f"{a} {b}" for a, b in pairs[:n]]
def tex(inp, out, kind, seed):
    if kind == "lp": LP.lp(inp, out, seed=seed)
    elif kind == "tape": TP.tape(inp, out, seed=seed)
    else: shutil.copy(inp, out)
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=60); ap.add_argument("--out", default="out/album"); ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--texture", default="lp", choices=["lp", "tape", "none"]); ap.add_argument("--moods", default="ballad90,minor80,citypop80"); ap.add_argument("--vol", type=int, default=1)
    ap.add_argument("--pad", type=float, default=.5, help="곡에 약한 패드를 얹을 확률 (0~1)"); ap.add_argument("--xfade", type=float, default=6.0)
    a = ap.parse_args(); rnd = random.Random(a.seed); moods = a.moods.split(",")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); tmp = tempfile.mkdtemp(prefix="album_"); cwd = os.getcwd(); os.chdir(tmp)
    X = int(a.xfade * SR); tracks = []; tail = None; pos = 0.0; last_mood = None; last_key = None
    outwav = os.path.join(cwd, a.out + ".wav"); w = sf.SoundFile(outwav, "w", SR, 2, subtype="PCM_16")
    used_scenes = {}; i = 0; plan = []
    for _ in range(int(a.minutes * 60 / 140) + 4):                      # 먼저 곡 구성을 정하고, 잔잔한 곡이 앞에 오도록 순서를 잡는다
        mood = rnd.choice([m for m in moods if m != last_mood] or moods); last_mood = mood
        key = rnd.choice([k for k in KEYS if k != last_key]); last_key = key
        pad = round(rnd.uniform(.08, .14), 2) if rnd.random() < a.pad else 0.0; bpm = rnd.randint(*BPM[mood])
        plan.append(dict(mood=mood, key=key, prog=rnd.choice(PROGS[mood]), bpm=bpm, seed=rnd.randint(1, 10 ** 6), pad=pad, lh=rnd.choice(["arp", "block"]) if mood != "citypop80" else "arp",
                         energy=bpm + ENERGY[mood] - (6 if pad else 0)))
    calm = sorted(plan, key=lambda q: q["energy"])[:3]; rest = [q for q in plan if q not in calm]; rnd.shuffle(rest)
    for _t in range(30):                                                  # 같은 분위기가 연속되지 않게 섞기
        if all(rest[k]["mood"] != rest[k + 1]["mood"] for k in range(len(rest) - 1)): break
        rnd.shuffle(rest)
    order = calm + rest                                                   # 첫 3곡은 가장 잔잔한 곡 (에너지 낮은 순)
    for q in order:
        if pos >= a.minutes * 60: break
        i += 1; mood, key, prog, bpm, seed, pad, lh = q["mood"], q["key"], q["prog"], q["bpm"], q["seed"], q["pad"], q["lh"]
        nm = f"t{i:02d}"; bg_prompt, title = SC.pick(mood, rnd, used_scenes)   # 장면과 제목을 함께 정함
        R.comp(nm, key, mood in MINOR, prog, bpm, seed, pad_vol=pad, lh=lh, swing=1 if mood == "citypop80" else 0)
        tex(f"{nm}.wav", f"{nm}_x.wav", a.texture, seed)
        d, _ = sf.read(f"{nm}_x.wav", dtype="float32"); d = d / max(1e-6, np.sqrt((d ** 2).mean())) * .12   # 곡마다 비슷한 음량
        os.makedirs(os.path.join(cwd, a.out + "_midi"), exist_ok=True); shutil.copy(f"{nm}.mid", os.path.join(cwd, a.out + "_midi", f"{nm}.mid"))   # 건반 비주얼용
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
        tracks.append(dict(i=i, title=title, title_en=SC.en_title(title), bg_prompt=bg_prompt, start=round(start, 2), dur=round(len(d) / SR, 2), midi=f"{os.path.basename(a.out)}_midi/{nm}.mid", mood=mood, key=key, bpm=bpm, pad=pad > 0, lh=lh))
        pos = start + len(d) / SR
    if tail is not None:
        w.write(np.clip(tail, -1, 1))
    w.close(); os.chdir(cwd); shutil.rmtree(tmp, ignore_errors=True)
    # 마지막으로 전체 음량을 맞춰 mp3 로 (ffmpeg loudnorm)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", outwav, "-af", "loudnorm=I=-18:TP=-2:LRA=9", "-b:a", "192k", a.out + ".mp3"], check=True)
    os.remove(outwav)
    json.dump(tracks, open(a.out + "_tracks.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    def ts(s): s = int(s); return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60:02d}:{s % 60:02d}"
    from collections import Counter
    cnt = Counter(t["mood"] for t in tracks); dom, n_dom = cnt.most_common(1)[0]; line1, line2 = HEAD[dom] if n_dom / len(tracks) >= .6 else MIXED
    ms = [m for m, _ in cnt.most_common()]; mins = int(round(pos / 60))
    intro = (f"{line1} {line2}. 가사 없는 연주곡 {mins}분.\n"
             f"잔잔한 곡으로 시작해 서서히 깊어지는 흐름입니다. 이번 앨범은 {INTRO[ms[0]]}" + (f"에 {INTRO[ms[1]]}이 더해진 곡들로 채웠습니다." if len(ms) > 1 else "의 곡들로 채웠습니다."))
    tags = list(TAGS)
    if "citypop80" in cnt: tags += ["시티팝", "city pop"]
    hashtags = "#80년대 #90년대 #피아노발라드 #BSideNight"
    head_en = HEAD_EN[dom] if n_dom / len(tracks) >= .6 else MIXED_EN
    intro_en = (f"{head_en}. Instrumental, no vocals. {mins} min.\nStarts quietly and slowly deepens. This album blends {INTRO_EN[ms[0]]}" + (f" with {INTRO_EN[ms[1]]}." if len(ms) > 1 else "."))
    tl = "\n".join(f"{ts(t['start'])} {t['title_en'] or t['title']}" for t in tracks); credit = "Piano samples: Salamander Grand Piano by Alexander Holm (CC BY 3.0)\nSynthesized music (AI / code-generated)."
    desc_en = intro_en + "\n\n" + tl + "\n\n" + credit + "\n\n#80s #90s #PianoBallad #BSideNight\n"
    desc = intro + "\n\n" + intro_en + "\n\n" + "\n".join(f"{ts(t['start'])} {t['title']}" + (f" ({t['title_en']})" if t['title_en'] else "") for t in tracks) + "\n\nPiano samples: Salamander Grand Piano by Alexander Holm (CC BY 3.0)\n합성 음악(AI·코드 생성)입니다.\n\n" + hashtags + "\n"
    open(a.out + "_description.txt", "w", encoding="utf-8").write(desc)
    title = f"{line1} {line2} ({head_en}) | Vol.{a.vol} | B-Side Night"; title_en = f"{head_en} | Vol.{a.vol} | B-Side Night"
    json.dump(dict(title=title, title_en=title_en, desc_en=desc_en, line1_en=head_en, line1=line1, line2=line2, tags=tags, vol=a.vol, minutes=mins), open(a.out + "_meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("제목:", title)
    print(f"완료: {len(tracks)}곡 약 {pos / 60:.1f}분 -> {a.out}.mp3")
if __name__ == "__main__":
    main()
