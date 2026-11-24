# -*- coding: utf-8 -*-
"""앨범 썸네일(1280x720): 첫 곡의 AI 배경 위에 큰 제목 + Vol 뱃지 + LP.
python thumbnail.py --tracks out/vol01_tracks.json --vol 1 --minutes 60 --out out/vol01_thumb.jpg [--line1 ... --line2 ...]"""
import argparse, json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import visual as V
W, H = 1280, 720
# 밤의 서사 테마별 색: accent=큰 글자/뱃지 색, tint=배경 색조(RGB 배율), sat=채도(1=그대로)
PAL = {"winter": ((170, 215, 255), (.85, .98, 1.22), .8), "rainy": ((120, 200, 225), (.80, .98, 1.12), .75), "happy": ((255, 214, 90), (1.15, 1.05, .82), 1.15),
       "anticipation": ((255, 170, 120), (1.12, .98, .90), 1.05), "flutter": ((255, 150, 195), (1.12, .90, 1.05), 1.1), "hard": ((205, 105, 95), (1.0, .82, .80), .6),
       "tired": ((180, 170, 215), (.92, .92, 1.0), .45), "blue": ((120, 145, 215), (.80, .90, 1.18), .5), "fire": ((255, 135, 50), (1.25, .90, .65), 1.2)}
def make(tracks_path, vol, minutes, out, line1, line2, lang="ko", theme="", head_en=""):
    mp = tracks_path.replace("_tracks.json", "_meta.json")      # 앨범 분위기에 맞춘 문구 (make_album 이 정함)
    if os.path.exists(mp) and not (line1 or line2):
        mt = json.load(open(mp, encoding="utf-8")); line1, line2 = mt["line1"], mt["line2"]; en = mt.get("line1_en", ""); theme = theme or mt.get("theme", "")
    else: en = ""
    if head_en: en = head_en
    if lang == "en": line1, line2 = (en.rsplit(" ", 2)[0], " ".join(en.split()[-2:])) if en else ("Late Night", "Piano Ballads")
    line1, line2 = line1 or "밤, 혼자 듣는", line2 or "80~90년대 피아노 발라드"
    tr = json.load(open(tracks_path, encoding="utf-8")) if os.path.exists(tracks_path) else []; base = os.path.dirname(os.path.abspath(tracks_path)); bgp = next((os.path.join(base, t["bg"]) for t in tr if t.get("bg") and os.path.exists(os.path.join(base, t["bg"]))), None)
    a = V.load_bg(bgp) if bgp else V.background(vol * 7 + 1); a = np.asarray(Image.fromarray(np.clip(a, 0, 255).astype("uint8")).resize((W, H), Image.LANCZOS)).astype("float32"); a = np.clip(a * 1.25, 0, 255)
    acc, tint, sat = PAL.get(theme, ((255, 196, 120), (1, 1, 1), 1.0))
    if theme in PAL:
        gray = a.mean(axis=2, keepdims=True); a = np.clip((gray + (a - gray) * sat) * np.array(tint)[None, None, :], 0, 255)          # 썸네일은 배경을 조금 더 밝게
    g = np.linspace(1, .25, W)[None, :, None]; a = a * (.55 + .45 * g)                               # 왼쪽(글자 쪽)을 더 어둡게
    im = Image.fromarray(a.astype("uint8")).convert("RGBA"); d = ImageDraw.Draw(im, "RGBA")
    rec = V.make_record(440, label=acc) if theme in PAL else V.make_record(440); sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([W - 520, H - 410, W - 60, H - 30], fill=(0, 0, 0, 140)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    im.alpha_composite(rec.rotate(-24, resample=Image.BICUBIC), (W - 500, H - 460))
    d.rounded_rectangle([70, 70, 70 + 250, 70 + 52], 26, fill=(acc[0] * 7 // 10, acc[1] * 7 // 10, acc[2] * 7 // 10, 235) if theme in PAL else (196, 74, 56, 235)); d.text((70 + 125, 70 + 26), f"VOL.{vol:02d} · {int(minutes)}{'분' if lang == 'ko' else ' MIN'}", font=V.F(28), fill=(255, 240, 220), anchor="mm")
    if theme in PAL:        # 테마 말(예: '비 오는 밤')을 크게 액센트 색으로, '에 듣는'과 둘째 줄은 작게/흰색
        key, rest = (line1.split("에 듣는", 1)[0], "에 듣는") if (lang == "ko" and "에 듣는" in line1) else (line1, "")
        ksz = (124 if len(key) <= 6 else (104 if len(key) <= 9 else 88)) if lang == "ko" else (100 if len(key) <= 14 else 78)
        for dx, dy in ((4, 4), (2, 2)): d.text((70 + dx, 250 + dy), key, font=V.F(ksz), fill=(0, 0, 0, 180), anchor="ls")
        d.text((70, 250), key, font=V.F(ksz), fill=acc, anchor="ls")
        if rest: d.text((70 + d.textlength(key, font=V.F(ksz)) + 10, 250), rest, font=V.F(52), fill=(255, 240, 214), anchor="ls")
        for dx, dy in ((3, 3), (2, 2)): d.text((70 + dx, 250 + 100 + dy), line2, font=V.F(58), fill=(0, 0, 0, 170), anchor="ls")
        d.text((70, 250 + 100), line2, font=V.F(58), fill=(255, 244, 226), anchor="ls")
    else:
        for k, (txt, sz, col) in enumerate(((line1, 86, (255, 240, 214)), (line2, 70, (255, 196, 120)))):
            y = 250 + k * 130
            for dx, dy in ((3, 3), (2, 2)): d.text((70 + dx, y + dy), txt, font=V.F(sz), fill=(0, 0, 0, 170), anchor="ls")
            d.text((70, y), txt, font=V.F(sz), fill=col, anchor="ls")
    if lang == "ko" and en: d.text((72, 250 + 130 + 62), en, font=V.F(34), fill=(235, 224, 205, 215), anchor="ls")      # 한글 썸네일에도 작은 영문 한 줄
    im.convert("RGB").save(out, quality=90); print("썸네일:", out)
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--tracks", default="none.json"); ap.add_argument("--vol", type=int, default=1); ap.add_argument("--minutes", type=float, default=60); ap.add_argument("--out", required=True)
    ap.add_argument("--line1", default=""); ap.add_argument("--line2", default=""); ap.add_argument("--lang", default="ko", choices=["ko", "en"]); ap.add_argument("--theme", default=""); ap.add_argument("--head-en", default=""); a = ap.parse_args(); make(a.tracks, a.vol, a.minutes, a.out, a.line1, a.line2, a.lang, a.theme, a.head_en)
