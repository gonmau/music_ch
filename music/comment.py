# -*- coding: utf-8 -*-
"""영상 첫 댓글(한글 + 영문)을 채널 이름으로 단다. 고정(핀)은 YouTube API가 지원하지 않아서 Studio에서 직접 눌러야 한다.
python comment.py --video-id XXXX [--theme flutter] [--text-file out/vol04_comment.txt]
환경변수: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (force-ssl 권한 필요). 호출당 약 50 할당량."""
import argparse, os
T = {   # 테마: (한글, 영문)
 "": ("오늘도 수고 많으셨어요. 불을 낮추고 편하게 들어 주세요 🎹\n지금 가장 좋아하는 80~90년대 발라드는 어떤 곡인가요?",
      "Thank you for staying up with us tonight. Turn the lights down and let the piano play.\nWhat's your favorite 80s/90s ballad?"),
 "winter": ("추운 겨울밤, 따뜻한 이불 속에서 들어 주세요.\n올겨울 가장 기억에 남는 순간은 무엇인가요? ❄️",
            "A quiet piano for the cold winter nights.\nWhat's your favorite memory of this winter?"),
 "rainy": ("비 오는 밤, 창가에 앉아 듣기 좋은 피아노입니다. 빗소리 없이 건반 소리만 담았어요.\n비 오는 날 떠오르는 노래가 있나요? ☔",
           "Piano for rainy nights, with no rain sounds, just the keys.\nWhat song comes to mind on a rainy day?"),
 "happy": ("기분 좋은 밤에 어울리는 곡들을 모았어요.\n오늘 좋았던 일 하나만 알려 주세요 ☺️",
           "Gentle piano for a happy night.\nTell us one good thing from your day."),
 "anticipation": ("기대되는 일이 있는 밤에 들어 주세요.\n요즘 기다리고 있는 일이 있나요?",
                  "For nights when you're looking forward to something.\nWhat are you waiting for these days?"),
 "flutter": ("설레는 마음으로 잠 못 드는 밤에 어울리는 곡들을 모았습니다.\n요즘 두근거리는 일이 있다면 살짝 알려 주세요 💗",
             "Piano for fluttering hearts on sleepless nights.\nIs there something that makes your heart race lately?"),
 "hard": ("힘든 하루였다면, 잠시 이 음악과 함께 쉬어 가세요.\n오늘도 정말 고생 많으셨어요.",
          "If today was hard, take a moment to rest with this music.\nYou did well to get through it."),
 "tired": ("지친 몸과 마음에 작은 쉼표가 되길 바랍니다.\n오늘 하루는 어땠나요?",
           "May this be a small pause for a tired mind.\nHow was your day?"),
 "blue": ("마음이 가라앉는 밤, 조용히 곁에 있어 드릴게요.\n지금 어떤 기분인지 편하게 적어 주세요.",
          "On blue nights, we'll quietly keep you company.\nFeel free to share how you feel."),
 "fire": ("불멍하듯 가만히 듣기 좋은 피아노입니다.\n오늘 밤 함께하는 따뜻한 음료가 있나요? 🔥",
          "Piano to listen to as if watching a fire.\nWhat warm drink are you having tonight?"),
}
def text_for(theme=""):
    ko, en = T.get(theme or "", T[""]); return f"{ko}\n\n{en}"
def post(yt, video_id, text):
    r = yt.commentThreads().insert(part="snippet", body={"snippet": {"videoId": video_id, "topLevelComment": {"snippet": {"textOriginal": text}}}}).execute()
    return r["id"]
def main():
    from upload import youtube
    ap = argparse.ArgumentParser(); ap.add_argument("--video-id", required=True); ap.add_argument("--theme", default=""); ap.add_argument("--text-file", default=""); a = ap.parse_args()
    text = open(a.text_file, encoding="utf-8").read().strip() if a.text_file and os.path.exists(a.text_file) else text_for(a.theme)
    try:
        cid = post(youtube(), a.video_id, text); print(f"댓글 등록: https://www.youtube.com/watch?v={a.video_id}&lc={cid}\n  고정은 Studio > 댓글에서 ⋮ > 고정 을 직접 눌러 주세요.")
    except Exception as e:
        print(f"댓글 실패: {str(e)[:300]}\n  (비공개/예약 상태에서는 달리지 않을 수 있습니다. 공개 후 music-comment 를 실행하세요.)")
if __name__ == "__main__":
    main()
