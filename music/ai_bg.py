# -*- coding: utf-8 -*-
"""곡마다 다른 아날로그 분위기 배경 이미지를 Cloudflare Workers AI(flux-1-schnell)로 만든다.
python ai_bg.py --tracks out/vol01_tracks.json [--force]
환경변수: CF_ACCOUNT_ID, CF_API_TOKEN. 결과: <앨범>_bg/tNN.jpg (1280x720) 와 tracks.json 의 bg 필드. 키가 없거나 한도(429)면 그 곡은 임시 배경으로 남는다.
곡 1개 = 이미지 1장 (1시간 앨범 약 24장). 사람·글자가 없는 장면만 쓴다."""
import argparse, base64, io, json, os, random, sys, time
from pathlib import Path
import requests
from PIL import Image
MODEL = "@cf/black-forest-labs/flux-1-schnell"
from scenes import STYLE, SCENES
def gen(prompt, session):
    acc, tok = os.environ["CF_ACCOUNT_ID"].strip(), os.environ["CF_API_TOKEN"].strip()
    r = session.post(f"https://api.cloudflare.com/client/v4/accounts/{acc}/ai/run/{MODEL}", headers={"Authorization": f"Bearer {tok}"}, json={"prompt": f"{prompt}. {STYLE}", "steps": 4}, timeout=120)
    if r.status_code == 429: raise RuntimeError("429")
    r.raise_for_status(); b = (r.json().get("result") or {}).get("image")
    if not b: raise RuntimeError("응답에 이미지 없음")
    return Image.open(io.BytesIO(base64.b64decode(b))).convert("RGB")
def to_wide(im, w=1280, h=720):      # 정사각 결과를 16:9 로 자르고 크기를 맞춘다 (배경이라 약간 흐려도 무방)
    W0, H0 = im.size; ch = int(W0 * h / w); top = int((H0 - ch) * .55); return im.crop((0, top, W0, top + ch))    # 원본 해상도를 그대로 둠 (화면 크기에 맞추는 건 영상 만들 때)
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tracks", required=True); ap.add_argument("--force", action="store_true"); ap.add_argument("--seed", type=int, default=1); a = ap.parse_args()
    if not (os.environ.get("CF_ACCOUNT_ID") and os.environ.get("CF_API_TOKEN")):
        sys.exit("Cloudflare 키가 없습니다. 빠진 환경변수: " + ", ".join(k for k in ("CF_ACCOUNT_ID", "CF_API_TOKEN") if not os.environ.get(k)))
    tp = Path(a.tracks); tracks = json.load(open(tp, encoding="utf-8")); rnd = random.Random(a.seed); stem = tp.name.replace("_tracks.json", ""); d = tp.parent / f"{stem}_bg"; d.mkdir(exist_ok=True)
    pools = SCENES; used = {m: 0 for m in SCENES}; s = requests.Session(); made = 0
    for t in tracks:
        m = t.get("mood", "ballad90"); pool = pools.get(m) or pools["ballad90"]; prompt = t.get("bg_prompt") or pool[used.get(m, 0) % len(pool)][0]; used[m] = used.get(m, 0) + 1
        dest = d / f"t{t['i']:02d}.jpg"; t["bg_prompt"] = prompt
        if dest.exists() and not a.force:
            t["bg"] = f"{stem}_bg/{dest.name}"; continue
        try:
            to_wide(gen(prompt, s)).save(dest, quality=88); t["bg"] = f"{stem}_bg/{dest.name}"; made += 1; print(f"  [{t['i']}] {prompt[:50]}")
        except Exception as e:
            print(f"  [{t['i']}] 실패({e}) -> 임시 배경 사용" + (" (한도 초과: 나머지도 건너뜀)" if "429" in str(e) else ""))
            if "429" in str(e): break
            time.sleep(3)
    json.dump(tracks, open(tp, "w", encoding="utf-8"), ensure_ascii=False, indent=1); print(f"완료: 새 이미지 {made}장 / 곡 {len(tracks)}개")
if __name__ == "__main__":
    main()
