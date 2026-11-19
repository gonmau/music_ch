# -*- coding: utf-8 -*-
"""음악 영상 비주얼 미리보기/렌더: 임시 배경 + (피아노 건반 | 돌아가는 LP | 둘 다 작게) + 곡 제목.
python visual.py --style keys|lp|both --midi a.mid --audio a.mp3 --start 20 --dur 22 --title "밤 열한 시의 피아노" --out prev_keys.mp4
건반은 MIDI의 실제 음 길이에 맞춰 눌리고 잔광이 남는다."""
import argparse, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import pretty_midi as pm
from pathlib import Path
W, H, FPS = 1280, 720, 24
FONT = str(Path(__file__).parent / "fonts" / "NanumMyeongjo-ExtraBold.ttf")
AMBER = (255, 196, 120)

def background(seed=3):
    rnd = np.random.RandomState(seed)
    y = np.linspace(0, 1, H)[:, None, None]; top = np.array([18, 24, 36]); bot = np.array([46, 30, 28])
    im = (top * (1 - y) + bot * y) * np.ones((H, W, 3))
    img = Image.fromarray(im.astype("uint8")); d = ImageDraw.Draw(img, "RGBA")
    for _ in range(26):                                  # 창밖 불빛 같은 흐린 빛망울
        x, yy, r = rnd.randint(0, W), rnd.randint(40, 420), rnd.randint(18, 70); c = tuple([[255, 190, 110], [255, 150, 90], [140, 170, 220]][rnd.randint(0, 3)]) + (int(rnd.randint(14, 40)),)
        d.ellipse([x - r, yy - r, x + r, yy + r], fill=c)
    img = img.filter(ImageFilter.GaussianBlur(14))
    a = np.asarray(img).astype("float32")
    yy, xx = np.ogrid[:H, :W]; v = 1 - .55 * (((xx - W / 2) / (W / 1.25)) ** 2 + ((yy - H / 2) / (H / 1.15)) ** 2); a *= np.clip(v, .25, 1)[..., None]   # 비네팅
    return a

def keyboard_layout(lo=36, hi=96, x0=90, x1=W - 90, ytop=0, h=120):
    whites = [m for m in range(lo, hi + 1) if m % 12 in (0, 2, 4, 5, 7, 9, 11)]; wk = (x1 - x0) / len(whites); pos = {}
    for i, m in enumerate(whites): pos[m] = (x0 + i * wk, wk, False)
    for m in range(lo, hi + 1):
        if m % 12 in (1, 3, 6, 8, 10) and (m - 1) in pos: pos[m] = (pos[m - 1][0] + wk * .68, wk * .64, True)
    return pos, h

def draw_keys(frame, pos, h, t, notes, ybase, scale=1.0):
    d = ImageDraw.Draw(frame, "RGBA"); act = {}
    for n in notes:                                       # 눌림 세기: 누르는 동안 1, 뗀 뒤 0.35초 동안 잔광
        if n.start <= t:
            e = 1.0 if t <= n.end else max(0.0, 1 - (t - n.end) / .35)
            if e > 0: act[n.pitch] = max(act.get(n.pitch, 0), e * (.6 + .4 * n.velocity / 127))
    for blk in (False, True):
        for m, (x, w, b) in pos.items():
            if b != blk: continue
            hh = h * (.62 if b else 1.0); e = act.get(m, 0)
            base = (28, 26, 30) if b else (222, 214, 200); col = tuple(int(base[i] * (1 - e) + AMBER[i] * e) for i in range(3))
            d.rectangle([x, ybase, x + w - 1.5, ybase + hh + (3 * e if not b else 0)], fill=col + (235,), outline=(10, 10, 12, 255))
            if e > .05: d.rectangle([x - 4, ybase - 14 * e, x + w + 2, ybase], fill=AMBER + (int(60 * e),))   # 위로 번지는 빛
    return frame

def make_record(size, title):
    S = size * 2; rec = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(rec)
    d.ellipse([0, 0, S - 1, S - 1], fill=(14, 14, 16, 255))
    for r in range(int(S * .24), int(S * .49), 6): d.ellipse([S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r], outline=(32, 32, 36, 255))
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)             # 돌 때 보이는 빛줄기
    for ang in (35, 215): sd.pieslice([0, 0, S - 1, S - 1], ang - 9, ang + 9, fill=(255, 255, 255, 34))
    rec = Image.alpha_composite(rec, sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(rec); lr = int(S * .17); d.ellipse([S / 2 - lr, S / 2 - lr, S / 2 + lr, S / 2 + lr], fill=(196, 74, 56, 255))
    f = ImageFont.truetype(FONT, int(S * .028)); d.text((S / 2, S / 2 - S * .02), "NIGHT PIANO", font=f, fill=(250, 226, 190), anchor="mm"); d.text((S / 2, S / 2 + S * .02), "SIDE A · 33 RPM", font=f, fill=(250, 226, 190), anchor="mm")
    d.ellipse([S / 2 - 7, S / 2 - 7, S / 2 + 7, S / 2 + 7], fill=(14, 14, 16, 255))
    return rec.resize((size, size), Image.LANCZOS)

def render(style, midi, audio, start, dur, title, out):
    notes = [n for i in pm.PrettyMIDI(midi).instruments for n in i.notes]
    bg = background(); rnd = np.random.RandomState(1); grains = [rnd.randn(H // 2, W // 2, 1).repeat(2, 0).repeat(2, 1).astype("float32") * 2.2 for _ in range(6)]
    fT = ImageFont.truetype(FONT, 34); fS = ImageFont.truetype(FONT, 20)
    rsize = 360 if style == "lp" else 250; rec = make_record(rsize, title) if style in ("lp", "both") else None
    pos, kh = keyboard_layout(h=130 if style == "keys" else 80)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-ss", str(start), "-t", str(dur), "-i", audio,
           "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", str(dur), out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(int(dur * FPS)):
        t = start + k / FPS; z = 1 + .03 * k / (dur * FPS)                      # 아주 천천히 확대
        a = bg if z == 1 else np.asarray(Image.fromarray(bg.astype("uint8")).resize((int(W * z), int(H * z)), Image.BILINEAR).crop((int(W * (z - 1) / 2), int(H * (z - 1) / 2), int(W * (z - 1) / 2) + W, int(H * (z - 1) / 2) + H))).astype("float32")
        fr = Image.fromarray(np.clip(a + grains[k % 6], 0, 255).astype("uint8")).convert("RGBA"); d = ImageDraw.Draw(fr, "RGBA")
        if style == "keys":
            d.text((90, 90), "지금 재생 중", font=fS, fill=(230, 200, 160, 190)); d.text((90, 124), title, font=fT, fill=(250, 236, 214, 255))
            draw_keys(fr, pos, kh, t, notes, H - 210)
        else:
            cx, cy = (W * .68, H * .42) if style == "lp" else (W * .70, H * .36)
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([cx - rsize / 2 - 14, cy - rsize / 2 + 8, cx + rsize / 2 + 14, cy + rsize / 2 + 30], fill=(0, 0, 0, 120)); fr = Image.alpha_composite(fr, sh.filter(ImageFilter.GaussianBlur(14)))
            r2 = rec.rotate(-(k / FPS) * 360 * .555, resample=Image.BICUBIC); fr.alpha_composite(r2, (int(cx - rsize / 2), int(cy - rsize / 2)))
            d = ImageDraw.Draw(fr, "RGBA"); px, py = cx + rsize * .62, cy - rsize * .55                      # 톤암
            d.line([(px, py), (cx + rsize * .22, cy - rsize * .08)], fill=(200, 196, 190, 255), width=7); d.ellipse([px - 16, py - 16, px + 16, py + 16], fill=(120, 116, 112, 255))
            d.text((90, 150 if style == "lp" else 110), "지금 재생 중", font=fS, fill=(230, 200, 160, 190)); d.text((90, 184 if style == "lp" else 144), title, font=fT, fill=(250, 236, 214, 255))
            if style == "both": draw_keys(fr, pos, kh, t, notes, H - 150)
        p.stdin.write(np.asarray(fr.convert("RGB")).tobytes())
    p.stdin.close(); p.wait(); print("완료:", out)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--style", default="keys", choices=["keys", "lp", "both"]); ap.add_argument("--midi", required=True); ap.add_argument("--audio", required=True)
    ap.add_argument("--start", type=float, default=0); ap.add_argument("--dur", type=float, default=20); ap.add_argument("--title", default="밤 열한 시의 피아노"); ap.add_argument("--out", required=True)
    a = ap.parse_args(); render(a.style, a.midi, a.audio, a.start, a.dur, a.title, a.out)
