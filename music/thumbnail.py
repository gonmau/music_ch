# -*- coding: utf-8 -*-
"""앨범 썸네일(1280x720): 첫 곡의 AI 배경 위에 큰 제목 + Vol 뱃지 + LP.
python thumbnail.py --tracks out/vol01_tracks.json --vol 1 --minutes 60 --out out/vol01_thumb.jpg [--line1 ... --line2 ...]"""
import argparse, json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import visual as V
W, H = 1280, 720
def make(tracks_path, vol, minutes, out, line1, line2, lang="ko"):
    mp = tracks_path.replace("_tracks.json", "_meta.json")      # 앨범 분위기에 맞춘 문구 (make_album 이 정함)
    if os.path.exists(mp) and not (line1 or line2):
        mt = json.load(open(mp, encoding="utf-8")); line1, line2 = mt["line1"], mt["line2"]; en = mt.get("line1_en", "")
    else: en = ""
    if lang == "en": line1, line2 = (en.rsplit(" ", 2)[0], " ".join(en.split()[-2:])) if en else ("Late Night", "Piano Ballads")
    line1, line2 = line1 or "밤, 혼자 듣는", line2 or "80~90년대 피아노 발라드"
    tr = json.load(open(tracks_path, encoding="utf-8")); base = os.path.dirname(os.path.abspath(tracks_path)); bgp = next((os.path.join(base, t["bg"]) for t in tr if t.get("bg") and os.path.exists(os.path.join(base, t["bg"]))), None)
    a = V.load_bg(bgp) if bgp else V.background(vol * 7 + 1); a = np.asarray(Image.fromarray(np.clip(a, 0, 255).astype("uint8")).resize((W, H), Image.LANCZOS)).astype("float32"); a = np.clip(a * 1.25, 0, 255)          # 썸네일은 배경을 조금 더 밝게
    g = np.linspace(1, .25, W)[None, :, None]; a = a * (.55 + .45 * g)                               # 왼쪽(글자 쪽)을 더 어둡게
    im = Image.fromarray(a.astype("uint8")).convert("RGBA"); d = ImageDraw.Draw(im, "RGBA")
    rec = V.make_record(440); sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([W - 520, H - 410, W - 60, H - 30], fill=(0, 0, 0, 140)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    im.alpha_composite(rec.rotate(-24, resample=Image.BICUBIC), (W - 500, H - 460))
    d.rounded_rectangle([70, 70, 70 + 250, 70 + 52], 26, fill=(196, 74, 56, 235)); d.text((70 + 125, 70 + 26), f"VOL.{vol:02d} · {int(minutes)}{'분' if lang == 'ko' else ' MIN'}", font=V.F(28), fill=(255, 240, 220), anchor="mm")
    for k, (txt, sz, col) in enumerate(((line1, 86, (255, 240, 214)), (line2, 70, (255, 196, 120)))):
        y = 250 + k * 130
        for dx, dy in ((3, 3), (2, 2)): d.text((70 + dx, y + dy), txt, font=V.F(sz), fill=(0, 0, 0, 170), anchor="ls")
        d.text((70, y), txt, font=V.F(sz), fill=col, anchor="ls")
    if lang == "ko" and en: d.text((72, 250 + 130 + 62), en, font=V.F(34), fill=(235, 224, 205, 215), anchor="ls")      # 한글 썸네일에도 작은 영문 한 줄
    im.convert("RGB").save(out, quality=90); print("썸네일:", out)
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--tracks", required=True); ap.add_argument("--vol", type=int, default=1); ap.add_argument("--minutes", type=float, default=60); ap.add_argument("--out", required=True)
    ap.add_argument("--line1", default=""); ap.add_argument("--line2", default=""); ap.add_argument("--lang", default="ko", choices=["ko", "en"]); a = ap.parse_args(); make(a.tracks, a.vol, a.minutes, a.out, a.line1, a.line2, a.lang)
