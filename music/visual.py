# -*- coding: utf-8 -*-
"""음악 영상 비주얼. 곡마다 스타일(건반 / LP / 건반+LP / 카세트 릴 / 주파수 막대)을 랜덤으로 바꾸고, 곡 사이는 부드럽게 섞는다.

앨범 영상:  python visual.py album --audio out/vol01.mp3 --tracks out/vol01_tracks.json --out out/vol01.mp4 [--seed 1] [--styles keys,lp,both,cassette,spectrum] [--w 1280 --h 720]
미리보기:   python visual.py preview --style lp --midi a.mid --audio a.mp3 --start 24 --dur 20 --out prev.mp4
건반은 MIDI의 실제 음 길이에 맞춰 눌리고, 주파수 막대는 실제 소리에서 계산한다. 배경은 곡마다 다른 임시 배경(나중에 AI 이미지로 교체)."""
import argparse, json, math, os, random, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import pretty_midi as pm

W, H, FPS = 1280, 720, 24
FONT = str(Path(__file__).parent / "fonts" / "NanumMyeongjo-ExtraBold.ttf")
AMBER = (255, 196, 120)
STYLES = ["keys", "lp", "both", "cassette", "spectrum"]
def F(sz): return ImageFont.truetype(FONT, int(sz))

def background(seed):
    rnd = np.random.RandomState(seed); pal = [([18, 24, 36], [46, 30, 28]), ([16, 28, 30], [40, 34, 24]), ([28, 20, 34], [50, 28, 26]), ([14, 20, 32], [34, 34, 40])][seed % 4]
    y = np.linspace(0, 1, H)[:, None, None]; im = (np.array(pal[0]) * (1 - y) + np.array(pal[1]) * y) * np.ones((H, W, 3))
    img = Image.fromarray(im.astype("uint8")); d = ImageDraw.Draw(img, "RGBA"); cols = [[255, 190, 110], [255, 150, 90], [140, 170, 220], [200, 130, 170]]
    for _ in range(26):
        x, yy, r = rnd.randint(0, W), rnd.randint(40, 420), rnd.randint(18, 70); d.ellipse([x - r, yy - r, x + r, yy + r], fill=tuple(cols[rnd.randint(0, 4)]) + (int(rnd.randint(14, 40)),))
    a = np.asarray(img.filter(ImageFilter.GaussianBlur(14))).astype("float32"); yy, xx = np.ogrid[:H, :W]
    return a * np.clip(1 - .55 * (((xx - W / 2) / (W / 1.25)) ** 2 + ((yy - H / 2) / (H / 1.15)) ** 2), .25, 1)[..., None]

def load_bg(path):
    """AI 배경 이미지를 1280x720으로 맞추고 어둡고 따뜻하게, 가장자리를 어둡게 (비주얼과 글자가 잘 보이도록)"""
    im = Image.open(path).convert("RGB").filter(ImageFilter.GaussianBlur(3)); w, h = im.size   # 약한 블러: 혹시 생긴 글자를 읽을 수 없게 + 아날로그 느낌
    r = max(W / w, H / h); im = im.resize((int(w * r) + 1, int(h * r) + 1), Image.LANCZOS)
    ox, oy = (im.width - W) // 2, (im.height - H) // 2; a = np.asarray(im.crop((ox, oy, ox + W, oy + H))).astype("float32") * .62
    a *= np.array([1.04, 1.0, .93]); yy, xx = np.ogrid[:H, :W]
    return a * np.clip(1 - .6 * (((xx - W / 2) / (W / 1.2)) ** 2 + ((yy - H / 2) / (H / 1.1)) ** 2), .3, 1)[..., None]

def keyboard_layout(lo=36, hi=96, x0=90, x1=W - 90):
    whites = [m for m in range(lo, hi + 1) if m % 12 in (0, 2, 4, 5, 7, 9, 11)]; wk = (x1 - x0) / len(whites); pos = {}
    for i, m in enumerate(whites): pos[m] = (x0 + i * wk, wk, False)
    for m in range(lo, hi + 1):
        if m % 12 in (1, 3, 6, 8, 10) and (m - 1) in pos: pos[m] = (pos[m - 1][0] + wk * .68, wk * .64, True)
    return pos

def draw_keys(fr, pos, h, t, notes, ybase):
    d = ImageDraw.Draw(fr, "RGBA"); act = {}
    for n in notes:
        if n.start <= t:
            e = 1.0 if t <= n.end else max(0.0, 1 - (t - n.end) / .35)
            if e > 0: act[n.pitch] = max(act.get(n.pitch, 0), e * (.6 + .4 * n.velocity / 127))
    for blk in (False, True):
        for m, (x, w, b) in pos.items():
            if b != blk: continue
            hh = h * (.62 if b else 1.0); e = act.get(m, 0); base = (28, 26, 30) if b else (222, 214, 200)
            d.rectangle([x, ybase, x + w - 1.5, ybase + hh + (3 * e if not b else 0)], fill=tuple(int(base[i] * (1 - e) + AMBER[i] * e) for i in range(3)) + (235,), outline=(10, 10, 12, 255))
            if e > .05: d.rectangle([x - 4, ybase - 14 * e, x + w + 2, ybase], fill=AMBER + (int(60 * e),))

def make_record(size):
    S = size * 2; rec = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(rec); d.ellipse([0, 0, S - 1, S - 1], fill=(14, 14, 16, 255))
    for r in range(int(S * .24), int(S * .49), 6): d.ellipse([S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r], outline=(32, 32, 36, 255))
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    for ang in (35, 215): sd.pieslice([0, 0, S - 1, S - 1], ang - 9, ang + 9, fill=(255, 255, 255, 34))
    rec = Image.alpha_composite(rec, sh.filter(ImageFilter.GaussianBlur(10))); d = ImageDraw.Draw(rec); lr = int(S * .17)
    d.ellipse([S / 2 - lr, S / 2 - lr, S / 2 + lr, S / 2 + lr], fill=(196, 74, 56, 255)); f = F(S * .028)
    d.text((S / 2, S / 2 - S * .06), "B-SIDE NIGHT", font=f, fill=(250, 226, 190), anchor="mm"); d.text((S / 2, S / 2 + S * .075), "SIDE B · 33 RPM", font=f, fill=(250, 226, 190), anchor="mm")
    d.ellipse([S / 2 - 7, S / 2 - 7, S / 2 + 7, S / 2 + 7], fill=(14, 14, 16, 255)); return rec.resize((size, size), Image.LANCZOS)

def draw_record(fr, rec, size, cx, cy, tl):
    sh = Image.new("RGBA", fr.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([cx - size / 2 - 14, cy - size / 2 + 8, cx + size / 2 + 14, cy + size / 2 + 30], fill=(0, 0, 0, 120))
    fr.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14))); fr.alpha_composite(rec.rotate(-tl * 360 * .555, resample=Image.BICUBIC), (int(cx - size / 2), int(cy - size / 2)))
    d = ImageDraw.Draw(fr, "RGBA"); px, py = cx + size * .62, cy - size * .55
    d.line([(px, py), (cx + size * .22, cy - size * .08)], fill=(200, 196, 190, 255), width=7); d.ellipse([px - 16, py - 16, px + 16, py + 16], fill=(120, 116, 112, 255))

def draw_cassette(fr, cx, cy, tl, prog, title):
    d = ImageDraw.Draw(fr, "RGBA"); w, h = 500, 320; x0, y0 = cx - w / 2, cy - h / 2
    d.rounded_rectangle([x0 + 8, y0 + 14, x0 + w + 8, y0 + h + 14], 18, fill=(0, 0, 0, 110))
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], 18, fill=(60, 56, 54, 255), outline=(20, 18, 18, 255), width=3)
    d.rounded_rectangle([x0 + 28, y0 + 22, x0 + w - 28, y0 + 140], 10, fill=(232, 214, 176, 255)); d.rectangle([x0 + 28, y0 + 22, x0 + w - 28, y0 + 50], fill=(196, 74, 56, 255))
    d.text((cx, y0 + 38), "SIDE B", font=F(18), fill=(250, 230, 200), anchor="mm"); d.text((cx, y0 + 96), title, font=F(24), fill=(60, 40, 30), anchor="mm")
    d.rounded_rectangle([x0 + 70, y0 + 165, x0 + w - 70, y0 + 255], 40, fill=(26, 24, 24, 255))
    for side, frac in ((-1, 1 - prog), (1, prog)):         # 테이프가 감기며 왼쪽 릴은 줄고 오른쪽 릴은 커짐
        rx = cx + side * 105; ry = y0 + 210; r = 20 + 22 * frac
        d.ellipse([rx - r, ry - r, rx + r, ry + r], fill=(70, 46, 34, 255)); d.ellipse([rx - 18, ry - 18, rx + 18, ry + 18], fill=(225, 220, 210, 255))
        for k in range(6):
            a = tl * 2 * math.pi * 1.1 * (1 if side > 0 else 1) + k * math.pi / 3; d.line([(rx + 5 * math.cos(a), ry + 5 * math.sin(a)), (rx + 17 * math.cos(a), ry + 17 * math.sin(a))], fill=(40, 38, 38, 255), width=4)
        d.ellipse([rx - 5, ry - 5, rx + 5, ry + 5], fill=(40, 38, 38, 255))
    d.polygon([(x0 + 150, y0 + h), (x0 + 175, y0 + h - 40), (x0 + w - 175, y0 + h - 40), (x0 + w - 150, y0 + h)], fill=(40, 38, 36, 255))

def spectrum_bars(audio, sr, t, prev, nb=56):
    i = int(t * sr); seg = audio[i:i + 2048]
    if len(seg) < 2048: seg = np.pad(seg, (0, 2048 - len(seg)))
    mag = np.abs(np.fft.rfft(seg * np.hanning(2048))); fr = np.fft.rfftfreq(2048, 1 / sr); edges = np.geomspace(60, 6500, nb + 1); out = np.zeros(nb)
    for k in range(nb):
        m = (fr >= edges[k]) & (fr < edges[k + 1]); out[k] = mag[m].mean() if m.any() else 0
    out = np.log1p(out * 5) / 4.5; out = np.clip(out, 0, 1); return np.maximum(out, prev * .86)

def draw_spectrum(fr, bars):
    d = ImageDraw.Draw(fr, "RGBA"); n = len(bars); cw, ch = fr.size; x0, x1, yb = 10, cw - 10, ch - 90; bw = (x1 - x0) / n
    for k, v in enumerate(bars):
        h = 8 + v * 270; x = x0 + k * bw; d.rounded_rectangle([x + 2, yb - h, x + bw - 2, yb], 3, fill=AMBER + (int(120 + 110 * v),))
        d.rounded_rectangle([x + 2, yb + 6, x + bw - 2, yb + 6 + h * .22], 3, fill=AMBER + (40,))      # 바닥 반사

CW, CH, WS = 800, 460, 2          # 위젯 캔버스(2배 크기로 그린 뒤 줄여 선명하게) -> 실제 400x230
MARGIN = 48

class Scene:
    def __init__(self, style, notes, title, seed, dur, corner="br", bg_path=None):
        self.style, self.notes, self.title, self.dur, self.corner = style, notes, title, dur, corner
        self.bg = load_bg(bg_path) if bg_path and os.path.exists(bg_path) else background(seed); self.pos = keyboard_layout(36, 96, 0, CW); self.bars = np.zeros(56)
        self.rec = make_record(400 if style == "lp" else 280) if style in ("lp", "both") else None
    def widget(self, tl, audio, sr, t_abs):
        w = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); s = self.style; R = self.corner == "br"      # 모서리 쪽으로 붙여 정렬
        if s == "keys": draw_keys(w, self.pos, 170, tl, self.notes, CH - 200)
        elif s == "lp": draw_record(w, self.rec, 400, CW - 250 if R else 250, CH * .5, tl)
        elif s == "both": draw_record(w, self.rec, 280, CW - 190 if R else 190, CH * .32, tl); draw_keys(w, self.pos, 110, tl, self.notes, CH - 140)
        elif s == "cassette": draw_cassette(w, CW - 255 if R else 255, CH / 2, tl, min(1, tl / max(1, self.dur)), self.title)
        elif s == "spectrum": self.bars = spectrum_bars(audio, sr, t_abs, self.bars); draw_spectrum(w, self.bars)
        return w.resize((CW // WS, CH // WS), Image.LANCZOS)
    def frame(self, tl, grain, audio=None, sr=16000, t_abs=0):
        z = 1 + .03 * min(1, tl / max(1, self.dur)); a = self.bg
        if z > 1:
            im = Image.fromarray(a.astype("uint8")).resize((int(W * z), int(H * z)), Image.BILINEAR); ox, oy = int(W * (z - 1) / 2), int(H * (z - 1) / 2); a = np.asarray(im.crop((ox, oy, ox + W, oy + H))).astype("float32")
        fr = Image.fromarray(np.clip(a + grain, 0, 255).astype("uint8")).convert("RGBA"); wd = self.widget(tl, audio, sr, t_abs)
        right = self.corner == "br"; wx = W - MARGIN - wd.width if right else MARGIN; wy = H - MARGIN - wd.height
        d = ImageDraw.Draw(fr, "RGBA")       # 제목은 좌상단에 작게 (우하단은 유튜브 워터마크 자리)
        sh = Image.new("RGBA", wd.size, (0, 0, 0, 0)); fr.alpha_composite(wd, (int(wx), int(wy)))
        d.text((MARGIN, MARGIN + 30), self.title, font=F(26), fill=(250, 236, 214, 235), anchor="ls")
        return fr

def load_audio(path, sr=16000):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(sr), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)

def encoder(audio, out, start=None, dur=None, w=W, h=H):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if start is not None: cmd += ["-ss", str(start), "-t", str(dur)]
    cmd += ["-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k"]
    if dur: cmd += ["-t", str(dur)]
    if (w, h) != (W, H): cmd[cmd.index("-c:v"):cmd.index("-c:v")] = ["-vf", f"scale={w}:{h}"]
    return subprocess.Popen(cmd + [out], stdin=subprocess.PIPE)

def grains(): 
    rnd = np.random.RandomState(1); return [rnd.randn(H // 2, W // 2, 1).repeat(2, 0).repeat(2, 1).astype("float32") * 2.2 for _ in range(6)]

def render_album(audio, tracks, out, seed=1, styles=None, base_dir=".", w=W, h=H, xfade=6.0, blend=1.5, corners="bl"):
    styles = styles or STYLES; rnd = random.Random(seed); sr = 16000; a16 = load_audio(audio, sr); gr = grains(); last = None; scenes = []
    for t in tracks:
        st = rnd.choice([s for s in styles if s != last] or styles); last = st; t["style"] = st
        mid = os.path.join(base_dir, t["midi"]); notes = [n for i in pm.PrettyMIDI(mid).instruments for n in i.notes]
        corner = corners if corners in ("br", "bl") else rnd.choice(["br", "bl"]); t["corner"] = corner
        scenes.append((t["start"], Scene(st, notes, t["title"], seed * 100 + t["i"], t["dur"], corner, os.path.join(base_dir, t["bg"]) if t.get("bg") else None), t["start"] + t["dur"]))
    total = len(a16) / sr; p = encoder(audio, out, w=w, h=h); bounds = [tracks[i + 1]["start"] + xfade / 2 for i in range(len(tracks) - 1)] + [1e9]
    for k in range(int(total * FPS)):
        T = k / FPS; g = gr[k % 6]
        def fr(j): return scenes[j][1].frame(max(0, T - scenes[j][0]), g, a16, sr, T).convert("RGB")
        near = next((j for j in range(len(bounds) - 1) if abs(T - bounds[j]) < blend / 2), None)
        if near is not None:       # 곡이 바뀌는 지점: 두 장면을 부드럽게 섞음
            f = Image.blend(fr(near), fr(near + 1), (T - bounds[near] + blend / 2) / blend)
        else:
            f = fr(next(j for j, bb in enumerate(bounds) if T < bb))
        p.stdin.write(np.asarray(f.convert("RGB")).tobytes())
        if k % (FPS * 300) == 0: print(f"  {T / 60:.0f}/{total / 60:.0f}분", flush=True)
    p.stdin.close(); p.wait(); print("완료:", out)

def render_preview(style, midi, audio, start, dur, title, out):
    notes = [n for i in pm.PrettyMIDI(midi).instruments for n in i.notes]; a16 = load_audio(audio); gr = grains(); sc = Scene(style, notes, title, 3, dur); p = encoder(audio, out, start, dur)
    for k in range(int(dur * FPS)): p.stdin.write(np.asarray(sc.frame(k / FPS, gr[k % 6], a16, 16000, start + k / FPS).convert("RGB")).tobytes())
    p.stdin.close(); p.wait(); print("완료:", out)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["album", "preview"]); ap.add_argument("--audio", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--tracks", default=""); ap.add_argument("--seed", type=int, default=1); ap.add_argument("--styles", default=",".join(STYLES)); ap.add_argument("--corner", default="bl", choices=["br", "bl", "random"], help="비주얼 위치: 우하단/좌하단/곡마다 랜덤"); ap.add_argument("--w", type=int, default=W); ap.add_argument("--h", type=int, default=H)
    ap.add_argument("--style", default="keys", choices=STYLES); ap.add_argument("--midi", default=""); ap.add_argument("--start", type=float, default=0); ap.add_argument("--dur", type=float, default=20); ap.add_argument("--title", default="밤 열한 시의 피아노")
    a = ap.parse_args()
    if a.mode == "album":
        tr = json.load(open(a.tracks, encoding="utf-8")); render_album(a.audio, tr, a.out, a.seed, a.styles.split(","), os.path.dirname(os.path.abspath(a.tracks)), a.w, a.h, corners=a.corner)
        json.dump(tr, open(a.out + ".styles.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    else:
        render_preview(a.style, a.midi, a.audio, a.start, a.dur, a.title, a.out)
