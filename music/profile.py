# -*- coding: utf-8 -*-
"""채널 프로필 이미지 시안 3종 (800x800, 유튜브가 원형으로 잘라 보여줌). python profile.py out/profile"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
import visual as V
S = 1600
def f(sz): return V.F(sz)
def bg(seed, c1, c2):
    y = np.linspace(0, 1, S)[:, None, None]; a = (np.array(c1) * (1 - y) + np.array(c2) * y) * np.ones((S, S, 3)); im = Image.fromarray(a.astype("uint8")).convert("RGBA"); d = ImageDraw.Draw(im, "RGBA"); r = np.random.RandomState(seed)
    for _ in range(14):
        x, yy, rr = r.randint(0, S), r.randint(0, S), r.randint(50, 130); d.ellipse([x - rr, yy - rr, x + rr, yy + rr], fill=(255, 190, 110, int(r.randint(4, 12))))
    return im.filter(ImageFilter.GaussianBlur(40))
def v1():       # LP: 검은 판 + 붉은 라벨 + B
    im = bg(1, (22, 26, 38), (40, 28, 28)); d = ImageDraw.Draw(im, "RGBA"); c = S // 2; R = 740
    d.ellipse([c - R, c - R, c + R, c + R], fill=(14, 14, 16, 255))
    for r in range(330, R - 10, 14): d.ellipse([c - r, c - r, c + r, c + r], outline=(34, 34, 38, 255), width=2)
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    for ang in (30, 210): sd.pieslice([c - R, c - R, c + R, c + R], ang - 10, ang + 10, fill=(255, 255, 255, 30))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(18))); d = ImageDraw.Draw(im, "RGBA"); L = 330
    d.ellipse([c - L, c - L, c + L, c + L], fill=(196, 74, 56, 255)); d.ellipse([c - L + 22, c - L + 22, c + L - 22, c + L - 22], outline=(250, 226, 190, 150), width=4)
    d.text((c, c - 30), "B", font=f(420), fill=(252, 232, 200), anchor="mm"); d.text((c, c + 190), "SIDE NIGHT", font=f(62), fill=(252, 232, 200), anchor="mm"); d.ellipse([c - 12, c - 330 + 30, c + 12, c - 330 + 54], fill=(14, 14, 16, 255)); return im
def v2():       # 미니멀: 따뜻한 배경 + 큰 B + 얇은 원
    im = bg(2, (34, 24, 30), (60, 34, 26)); d = ImageDraw.Draw(im, "RGBA"); c = S // 2
    d.ellipse([c - 700, c - 700, c + 700, c + 700], outline=(255, 196, 120, 200), width=8); d.ellipse([c - 640, c - 640, c + 640, c + 640], outline=(255, 196, 120, 80), width=3)
    d.text((c, c - 50), "B", font=f(780), fill=(255, 196, 120), anchor="mm"); d.text((c, c + 420), "SIDE NIGHT", font=f(96), fill=(255, 236, 210), anchor="mm"); return im
def v3():       # 초승달 + 밤하늘 + 이름
    im = bg(3, (12, 18, 34), (28, 30, 48)); d = ImageDraw.Draw(im, "RGBA"); c = S // 2; r = np.random.RandomState(5)
    for _ in range(60): x, y = r.randint(120, S - 120), r.randint(120, 900); d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 240, 210, int(r.randint(60, 200))))
    m = Image.new("L", (S, S), 0); md = ImageDraw.Draw(m); md.ellipse([c - 330, 250, c + 330, 910], fill=255); md.ellipse([c - 130, 200, c + 450, 780], fill=0)      # 초승달 (마스크)
    im.paste(Image.new("RGBA", (S, S), (255, 205, 130, 255)), (0, 0), m); d = ImageDraw.Draw(im, "RGBA")
    d.text((c, 1130), "B-SIDE", font=f(190), fill=(255, 236, 210), anchor="mm"); d.text((c, 1330), "NIGHT", font=f(190), fill=(255, 196, 120), anchor="mm"); return im
if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else "out/profile"
    for i, fn in enumerate((v1, v2, v3), 1): fn().convert("RGB").resize((800, 800), Image.LANCZOS).save(f"{base}{i}.png"); print(f"{base}{i}.png")
