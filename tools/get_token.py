# -*- coding: utf-8 -*-
# B-Side Night(음악 채널) 전용 토큰 받기. client_secret.json(구글 클라우드 OAuth 클라이언트)을 이 파일과 같은 폴더에 두고 get_token.bat 실행.
# 로그인 후 "채널 선택" 화면에서 반드시 B-Side Night 채널을 고르세요. 파일을 저장하지 않고 화면에만 출력합니다.
import os, sys
from google_auth_oauthlib.flow import InstalledAppFlow
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly",
          "https://www.googleapis.com/auth/yt-analytics.readonly", "https://www.googleapis.com/auth/youtube.force-ssl"]
secret = sys.argv[1] if len(sys.argv) > 1 else "client_secret.json"
if not os.path.exists(secret):
    raise SystemExit(f"{secret} 파일이 없습니다. 구글 클라우드에서 받은 OAuth 클라이언트 JSON을 이 폴더에 client_secret.json 이름으로 두세요.")
creds = InstalledAppFlow.from_client_secrets_file(secret, SCOPES).run_local_server(port=0, access_type="offline", prompt="consent")
print("\n아래 3개를 GitHub Secrets(music_ch)에 넣으세요")
print("YT_CLIENT_ID     =", creds.client_id)
print("YT_CLIENT_SECRET =", creds.client_secret)
print("YT_REFRESH_TOKEN =", creds.refresh_token)
