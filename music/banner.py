# -*- coding: utf-8 -*-
"""채널 배너 2560x1440 (모든 기기에서 보이는 안전 영역은 가운데 1546x423). python banner.py out/banner.png"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
import visual as V
W, H = 2560, 1440
def main(out):
    bg = V.background(11); im = Image.fromarray(np.clip(np.asarray(Image.fromarray(bg.astype("uint8")).resize((W, H), Image.LANCZOS)).astype("float32") * 1.3, 0, 255).astype("uint8")).convert("RGBA")
    d = ImageDraw.Draw(im, "RGBA"); cx, cy = W // 2, H // 2
    rec = V.make_record(900); sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([cx + 330, cy - 440, cx + 1230, cy + 480], fill=(0, 0, 0, 120)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30)))
    im.alpha_composite(rec.rotate(-30, resample=Image.BICUBIC), (cx + 330, cy - 450))          # 안전 영역 오른쪽, 일부는 바깥으로
    for txt, sz, y, col in (("B-SIDE NIGHT", 150, cy - 10, (255, 240, 214)), ("밤, 혼자, LP로 듣는 80~90년대 피아노", 54, cy + 80, (255, 196, 120)), ("매주 1시간 · 가사 없는 연주곡 플레이리스트", 40, cy + 150, (235, 215, 185))):
        for dx in (4,): d.text((cx - 760 + dx, y + dx), txt, font=V.F(sz), fill=(0, 0, 0, 160), anchor="ls")
        d.text((cx - 760, y), txt, font=V.F(sz), fill=col, anchor="ls")
    im.convert("RGB").save(out, quality=92); print(out)
if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out/banner.png")
