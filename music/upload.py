# -*- coding: utf-8 -*-
"""앨범 영상을 유튜브에 비공개로 올리고(예약 공개 선택) 썸네일을 설정한다.
python upload.py --video out/vol01.mp4 --thumb out/vol01_thumb.jpg --title "..." --desc out/vol01_description.txt [--publish-at "2026-11-26 20:00"]
환경변수: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (이 음악 채널 전용 토큰). --publish-at 은 한국시간."""
import argparse, os, time
from datetime import datetime, timedelta, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
TAGS = ["피아노", "연주곡", "발라드", "80년대", "90년대", "LP", "카세트", "플레이리스트", "뉴에이지", "밤", "감성", "piano", "ballad", "80s", "90s", "lofi"]
def youtube():
    c = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"], token_uri="https://oauth2.googleapis.com/token", client_id=os.environ["YT_CLIENT_ID"], client_secret=os.environ["YT_CLIENT_SECRET"])
    return build("youtube", "v3", credentials=c)
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--video", required=True); ap.add_argument("--thumb", default=""); ap.add_argument("--title", required=True); ap.add_argument("--desc", required=True); ap.add_argument("--publish-at", default=""); a = ap.parse_args()
    desc = open(a.desc, encoding="utf-8").read(); yt = youtube()
    body = {"snippet": {"title": a.title[:100], "description": desc[:4900], "categoryId": "10", "tags": TAGS},
            "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True}}
    if a.publish_at.strip():
        kst = datetime.strptime(a.publish_at.strip(), "%Y-%m-%d %H:%M").replace(tzinfo=timezone(timedelta(hours=9))); body["status"]["publishAt"] = kst.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    def ins(b):
        req = yt.videos().insert(part="snippet,status", body=b, media_body=MediaFileUpload(a.video, mimetype="video/mp4", resumable=True, chunksize=64 * 1024 * 1024)); res = None
        while res is None:
            st, res = req.next_chunk()
            if st: print(f"  업로드 {int(st.progress() * 100)}%", flush=True)
        return res
    try:
        res = ins(body)
    except Exception as e:
        if "containsSyntheticMedia" in str(e) or "synthetic" in str(e).lower():       # 이 필드를 지원하지 않는 경우 빼고 다시
            body["status"].pop("containsSyntheticMedia", None); res = ins(body); print("  ⚠ 합성 콘텐츠 표시를 API로 못 넣었습니다. Studio에서 직접 켜주세요.")
        else:
            raise
    vid = res["id"]; print(f"업로드(비공개{', 예약 ' + a.publish_at if a.publish_at else ''}): https://youtu.be/{vid}")
    if a.thumb and os.path.exists(a.thumb):
        for t in range(3):                  # 처리 중 덮어쓰기에 대비해 간격을 두고 다시 설정
            if t: time.sleep(60)
            try:
                yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(a.thumb, mimetype="image/jpeg")).execute(); print(f"  썸네일 설정 {t + 1}/3")
            except Exception as e:
                print(f"  썸네일 실패: {str(e)[:200]}"); break
    open("uploaded.txt", "w").write(vid)
if __name__ == "__main__":
    main()
