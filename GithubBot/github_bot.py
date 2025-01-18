import os
from dotenv import load_dotenv
load_dotenv()
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

@app.command("/conv-issue")
def conv_issue(ack):
    ack("""
최상단 디렉토리에 .github/ISSUE_TEMPLATE/(템플릿명).yml 파일을 생성한 후 아래 내용을 붙여넣습니다:
____________________________________________
name: "🆕 Feature"
description: "봇 추가"
title: "[Feat]: 00 기능 구현"
labels: "feature"
body:
  - type: input
    attributes:
      label: "🤖 설명"
      description: "추가하려는 기능"
      placeholder: "추가하려는 봇에 대한 한줄 설명"
    validations:
      required: false

  - type: textarea
    attributes:
      label: "📋 할일"
      description: "구현 to-do"
      placeholder: |
        - [ ] 앞에 적으면 체크리스트가 됩니다.
        - [x] 적으면 완료 항목으로 표시됩니다.
    validations:
      required: true

  - type: input
    attributes:
      label: "📆 기한"
      description: "예상 개발 완료 날짜"
      placeholder: "2025-01-01"
    validations:
      required: true

  - type: dropdown
    attributes:
      label: "❗️ 우선"
      options:
        - "1순위"
        - "2순위"
        - "부가 기능"

  - type: textarea
    attributes:
      label: "📝 메모"
      placeholder: "참고 자료 링크나 부가적으로 필요한 자원이 있다면 메모하세요"
        """)

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