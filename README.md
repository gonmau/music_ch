# music_ch — 밤, 혼자, 카세트·LP로 듣는 80~90년대 피아노 발라드

주 1회 장편(1시간 안팎) 플레이리스트를 코드로 합성해 만드는 음악 채널.

## 구성 (`music/`)
- `pianosynth.py` : Salamander Grand Piano 샘플로 MIDI → 오디오 (샘플은 저장소에 없음. `SALAMANDER_DIR` 로 폴더 지정)
- `retro.py` : 80~90년대 발라드/시티팝/단조 발라드 작곡 (`comp(...)`)
- `album.py` : 여러 곡을 키·템포·진행을 바꿔 크로스페이드로 이어 붙임
- `tape.py` : 카세트 질감 (속도 흔들림·고음 감쇠·포화·히스)
- `lp.py` : LP 질감 (안정된 음정·표면 소음·틱·팝). 현재 선택한 방향
- `make_album.py` : **1시간 앨범 만들기** (곡 합성→LP 질감→크로스페이드→mp3+곡목록+타임스탬프 설명). 예: `SALAMANDER_DIR=... python make_album.py --minutes 60 --out out/vol01 --seed 1`
- `calm2.py` : 패드 레이어 등 공용 (빗소리·물소리 함수는 이 채널에서는 쓰지 않음)

## 크레딧 (업로드 설명에 꼭 넣을 것)
Piano samples: Salamander Grand Piano by Alexander Holm (CC BY 3.0)
음악은 코드로 합성한 AI·합성 콘텐츠이므로 유튜브 업로드 때 합성 콘텐츠 표시를 켠다.

## 자동 제작 (GitHub Actions: music-album)
폰의 GitHub 앱 → Actions → **music-album** → Run workflow. 입력: 회차, 길이(분), 곡 분위기, 질감(LP/카세트), 비주얼 위치, AI 배경, 업로드 여부, 예약 공개 시각(한국시간).
흐름: `make_album.py`(곡) → `ai_bg.py`(곡마다 배경) → `visual.py`(영상, 곡마다 비주얼 랜덤) → `thumbnail.py` → `upload.py`(비공개 업로드·썸네일·합성 콘텐츠 표시).
Secrets: `CF_ACCOUNT_ID`, `CF_API_TOKEN`(AI 배경), `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`(이 음악 채널 전용 토큰, 썸네일까지 쓰려면 force-ssl 권한 포함), `DISCORD_WEBHOOK_URL`(선택).
피아노 샘플은 실행 때 `sfzinstruments/SalamanderGrandPiano` 를 받아 캐시한다.
