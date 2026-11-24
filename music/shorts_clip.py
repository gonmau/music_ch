# -*- coding: utf-8 -*-
"""앨범 영상에서 세로 쇼츠(1080x1920, 약 45초)를 잘라 만든다: 곡마다 한 줄 서사(KO/EN)와 곡 제목을 얹고, 설명란에 롱폼 링크를 넣을 txt 도 함께 만든다.
python shorts_clip.py --video out/vol04.mp4 --tracks out/vol04_tracks.json --vol 4 --n 3 [--dur 45] [--long-url https://youtu.be/xxxx]
결과: out/vol04_short1.mp4, out/vol04_short1.txt (제목 첫 줄, 이후 설명) ..."""
import argparse, os, subprocess, json, tempfile, textwrap
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NanumMyeongjo-ExtraBold.ttf")
TAGS = "#Shorts #피아노 #밤 #80년대 #BSideNight #PianoBallad"

def wrap(s, n):
    return "\n".join(textwrap.wrap(s, n, break_long_words=True)) if s else ""

def pick(tracks, n, dur):
    ok = [i for i, t in enumerate(tracks) if t.get("dur", 0) >= dur + 20] or list(range(len(tracks)))
    body = ok[1:-1] if len(ok) > 4 else ok          # 맨 처음(바늘 소리)·마지막 곡은 가급적 피함
    n = min(n, len(body)); step = len(body) / n
    return [body[int(k * step + step / 2)] for k in range(n)]

def txt(s):
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8"); f.write(s); f.close(); return f.name.replace("\\", "/")

def dt(path, size, y, color, t0, t1, fade=1.0, x="(w-text_w)/2"):
    al = f"if(lt(t,{t0}),0,if(lt(t,{t0 + fade}),(t-{t0})/{fade},if(lt(t,{t1 - fade}),1,if(lt(t,{t1}),({t1}-t)/{fade},0))))"
    return (f"drawtext=fontfile='{FONT}':textfile='{path}':fontsize={size}:fontcolor={color}:alpha='{al}':x={x}:y={y}:line_spacing=14:"
            f"shadowcolor=black@0.7:shadowx=2:shadowy=2")

def make(video, t, start, dur, out):
    parts = []
    parts.append(dt(txt("밤의 B면 · B-Side Night"), 40, 150, "0xF5E6CF", 0.3, dur, 0.8))
    parts.append(dt(txt(t.get("title", "")), 64, 1330, "0xFAECD6", 0.8, dur, 1.0))
    if t.get("title_en"):
        parts.append(dt(txt(t["title_en"]), 36, 1420, "0xE6D6BC", 1.2, dur, 1.0))
    if t.get("cap"):
        parts.append(dt(txt(wrap(t["cap"], 16)), 46, 1520, "0xF0E2CC", 4.0, dur - 3, 1.2))
    if t.get("cap_en"):
        parts.append(dt(txt(wrap(t["cap_en"], 34)), 30, 1700, "0xDCCFB8", 5.0, dur - 3, 1.2))
    vf = ("[0:v]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:6,eq=brightness=-0.22[bg];"
          "[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2-80[v];[v]" + ",".join(parts) + "[o]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(start), "-t", str(dur), "-i", video, "-filter_complex", vf, "-map", "[o]", "-map", "0:a",
                    "-af", f"afade=t=in:d=0.6,afade=t=out:st={dur - 1.8}:d=1.8", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
                    "-r", "30", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out], check=True)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--video", required=True); ap.add_argument("--tracks", required=True); ap.add_argument("--vol", default="1")
    ap.add_argument("--n", type=int, default=3); ap.add_argument("--dur", type=float, default=45); ap.add_argument("--long-url", default=""); ap.add_argument("--out", default="")
    a = ap.parse_args()
    tracks = json.load(open(a.tracks, encoding="utf-8")); base = a.out or os.path.splitext(a.video)[0]
    for k, i in enumerate(pick(tracks, a.n, a.dur), 1):
        t = tracks[i]; start = t["start"] + (6 if i else 5)
        out = f"{base}_short{k}.mp4"; make(a.video, t, start, a.dur, out)
        title = f"{t.get('title', '')} ({t['title_en']})" if t.get("title_en") else t.get("title", "")
        desc = (f"“{t['cap']}”\n“{t.get('cap_en', '')}”\n\n" if t.get("cap") else "") + \
               (f"전체 앨범 풀버전 / Full album: {a.long_url}\n\n" if a.long_url else "") + f"밤의 B면 · B-Side Night — 80~90년대 피아노 발라드, 가사 없는 연주곡\n{TAGS}\n"
        open(f"{base}_short{k}.txt", "w", encoding="utf-8").write(f"{(title + ' #Shorts')[:100]}\n{desc}")
        print(f"쇼츠 {k}: 곡{i + 1} {t.get('title', '')} -> {out}")
if __name__ == "__main__":
    main()
