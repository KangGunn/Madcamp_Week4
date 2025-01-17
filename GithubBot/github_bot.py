import os
from dotenv import load_dotenv
load_dotenv()

# from venv import logger
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)

# client = WebClient(token=SLACK_BOT_TOKEN)

channel_id = "C089G7VKG5P"      # '튜토리얼' 채널

@app.command("/conv-commit")
def conv_commit(ack):
    ack("Github 커밋 메세지 제목 컨벤션 : \'[TAG]: [영어는 명령형, 한국어는 명사형 문장] \' ")

@app.event("message")
def say_hi(body, say):
    # 사용자 ID 가져오기
    user_id = body.get("event", {}).get("user", "unknown user")
    text = body.get("event", {}).get("text", "")
    bot_id = app.client.auth_test()["user_id"]
    
    # 봇이 스스로의 메시지에 반응하지 않도록 필터링
    if user_id != "USLACKBOT" and f"<@{bot_id}>" not in text:
        say(f"<@{user_id}> 님, 오늘도 힘내세요!")

@app.event("app_mention")
def mention_test(say):
    say("왜여")

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()