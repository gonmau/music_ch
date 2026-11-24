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

KW = [("rain", "rain window night"), ("snow", "snow night window"), ("fireplace", "fireplace fire night"), ("fire", "campfire night"), ("candle", "candle night"), ("train", "train station night"), ("subway", "subway night"),
      ("street", "empty street night"), ("lamp", "street lamp night"), ("moon", "moon night sky"), ("ocean", "ocean night"), ("sea", "sea night"), ("forest", "forest night"), ("cafe", "cafe night window"),
      ("bridge", "bridge night city"), ("city", "city night lights"), ("window", "window night room"), ("room", "room night lamp"), ("piano", "piano room dim"), ("cassette", "vintage cassette"), ("record", "vinyl record")]
def pixabay(prompt, rnd, session, tried=()):
    """Cloudflare 한도 초과/실패 때: Pixabay 에서 비슷한 밤 분위기 사진을 가져온다 (PIXABAY_API_KEY 필요). 사람 사진은 피하려고 풍경/사물 검색어만 씀."""
    key = os.environ.get("PIXABAY_API_KEY", "").strip()
    if not key: return None
    low = prompt.lower(); q = next((v for k, v in KW if k in low), "night bokeh lights")
    r = session.get("https://pixabay.com/api/", params={"key": key, "q": q, "image_type": "photo", "orientation": "horizontal", "min_width": 1600, "safesearch": "true", "per_page": 30, "order": "popular"}, timeout=30)
    r.raise_for_status(); hits = [h for h in r.json().get("hits", []) if h["id"] not in tried]
    if not hits: return None
    h = rnd.choice(hits[:20]); im = Image.open(io.BytesIO(session.get(h["largeImageURL"], timeout=60).content)).convert("RGB")
    return im, {"source": "pixabay", "id": h["id"], "user": h.get("user", ""), "page": h.get("pageURL", ""), "q": q}
def to_wide(im, w=1280, h=720):      # 정사각 결과를 16:9 로 자르고 크기를 맞춘다 (배경이라 약간 흐려도 무방)
    W0, H0 = im.size; ch = int(W0 * h / w); top = int((H0 - ch) * .55); return im.crop((0, top, W0, top + ch))    # 원본 해상도를 그대로 둠 (화면 크기에 맞추는 건 영상 만들 때)
def notify(msg):
    print(msg, flush=True)
    url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if url:
        try: requests.post(url, json={"content": msg[:1900]}, timeout=15)
        except Exception: pass
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tracks", required=True); ap.add_argument("--force", action="store_true"); ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--source", default="ai", choices=["ai", "auto", "pixabay"], help="ai=Cloudflare AI (한도 초과되면 알림 후 전체를 Pixabay 로 다시), pixabay=처음부터 Pixabay"); a = ap.parse_args()
    has_cf = bool(os.environ.get("CF_ACCOUNT_ID") and os.environ.get("CF_API_TOKEN")) and a.source != "pixabay"
    has_px = bool(os.environ.get("PIXABAY_API_KEY"))
    if not has_cf and not has_px:
        sys.exit("Cloudflare 키(CF_ACCOUNT_ID, CF_API_TOKEN)도 Pixabay 키(PIXABAY_API_KEY)도 없습니다. 임시 배경으로 진행합니다.")
    tp = Path(a.tracks); tracks = json.load(open(tp, encoding="utf-8")); rnd = random.Random(a.seed); stem = tp.name.replace("_tracks.json", ""); d = tp.parent / f"{stem}_bg"; d.mkdir(exist_ok=True)
    pools = SCENES; used = {m: 0 for m in SCENES}; s = requests.Session(); made = 0
    def prompt_of(t):
        m = t.get("mood", "ballad90"); pool = pools.get(m) or pools["ballad90"]; pr = t.get("bg_prompt") or pool[used.get(m, 0) % len(pool)][0]; used[m] = used.get(m, 0) + 1; t["bg_prompt"] = pr; return pr
    def all_pixabay(why):          # 앨범 전체를 Pixabay 사진으로 (통일감을 위해 AI 로 만든 것도 다시 받는다)
        nonlocal made
        tried, ok = set(), 0
        for t in tracks:
            dest = d / f"t{t['i']:02d}.jpg"; pr = t.get("bg_prompt") or prompt_of(t)
            try:
                got = pixabay(pr, rnd, s, tried)
                if got:
                    tried.add(got[1]["id"]); to_wide(got[0]).save(dest, quality=88); t["bg"] = f"{stem}_bg/{dest.name}"; t["bg_credit"] = got[1]; ok += 1; continue
            except Exception as e:
                print(f"  [{t['i']}] Pixabay 실패({str(e)[:60]})")
            t.pop("bg", None); t.pop("bg_credit", None)
            try: dest.unlink()
            except OSError: pass
            print(f"  [{t['i']}] 이미지를 못 구해 임시 배경 사용")
        made += ok; print(f"Pixabay {ok}/{len(tracks)}곡 ({why})")
    if not has_cf:
        all_pixabay("Pixabay 선택"); json.dump(tracks, open(tp, "w", encoding="utf-8"), ensure_ascii=False, indent=1); return
    for t in tracks:
        prompt = prompt_of(t); dest = d / f"t{t['i']:02d}.jpg"
        if dest.exists() and not a.force:
            t["bg"] = f"{stem}_bg/{dest.name}"; continue
        try:
            to_wide(gen(prompt, s)).save(dest, quality=88); t["bg"] = f"{stem}_bg/{dest.name}"; made += 1; print(f"  [{t['i']}] {prompt[:50]}")
        except Exception as e:
            if "429" in str(e):
                if has_px:
                    notify(f"⚠️ music 배경: Cloudflare 한도 초과(곡 {t['i']}/{len(tracks)}). 통일감을 위해 전체 {len(tracks)}곡을 Pixabay 사진으로 다시 받아 렌더링합니다.")
                    all_pixabay("Cloudflare 한도 초과")
                else:
                    notify(f"⚠️ music 배경: Cloudflare 한도 초과(곡 {t['i']}/{len(tracks)}). PIXABAY_API_KEY가 없어 남은 곡은 임시 배경으로 진행합니다.")
                break
            print(f"  [{t['i']}] Cloudflare 실패({str(e)[:60]}) -> 임시 배경 사용"); time.sleep(3)
    json.dump(tracks, open(tp, "w", encoding="utf-8"), ensure_ascii=False, indent=1); print(f"완료: 새 이미지 {made}장 / 곡 {len(tracks)}개")
if __name__ == "__main__":
    main()
