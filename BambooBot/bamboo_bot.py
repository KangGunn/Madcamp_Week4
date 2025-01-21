import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
BAMBOO_CHANNEL_ID = os.getenv("BAMBOO_CHANNEL_ID")

# 대나무숲 글 번호를 저장할 파일 (없으면 생성됨)
COUNTER_FILE = "snitch_counter.txt"

# Slack 앱 초기화
app = App(token=SLACK_BOT_TOKEN)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.command("/꼰지르기")
def snitch(ack, body, client):
    ack()  # 요청 확인 응답

    # 모달 열기 (각 입력 블록에 block_id를 추가)
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "snitch_modal",
            "title": {
                "type": "plain_text",
                "text": "대나무숲 작성",
                "emoji": True
            },
            "submit": {
                "type": "plain_text",
                "text": "제출",
                "emoji": True
            },
            "close": {
                "type": "plain_text",
                "text": "취소",
                "emoji": True
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "plain_text_input_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "plain_text_input-action",
                        "multiline": True
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "대나무숲에 말할 내용을 적어주세요.",
                        "emoji": True
                    }
                },
                {
                    "type": "input",
                    "block_id": "name_input_block",
                    "optional": True,
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "name_input-action",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "입력하지 않을 시 익명으로 업로드 됩니다."
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "표시될 작성자의 이름",
                        "emoji": True
                    }
                }
            ]
        }
    )


@app.view("snitch_modal")
def handle_modal_submission(ack, body, client):
    ack()  # 요청 확인 응답

    # 사용자가 입력한 값 가져오기
    state_values = body["view"]["state"]["values"]
    try:
        message = state_values["plain_text_input_block"]["plain_text_input-action"]["value"]
    except KeyError:
        message = ""
    
    # 이름 입력 필드에서 value가 존재하는지 안전하게 확인
    name = state_values.get("name_input_block", {}).get("name_input-action", {}).get("value")
    if name is not None:
        name = name.strip()
    else:
        name = ""
    if not name:
        name = "익명"

    # 글 번호 증가를 위한 함수 (파일에 저장)
    def get_next_counter():
        try:
            if os.path.exists(COUNTER_FILE):
                with open(COUNTER_FILE, "r", encoding="utf-8") as f:
                    count = int(f.read().strip())
            else:
                count = 0
        except Exception as e:
            logger.error(f"Counter file read error: {e}")
            count = 0
        count += 1
        try:
            with open(COUNTER_FILE, "w", encoding="utf-8") as f:
                f.write(str(count))
        except Exception as e:
            logger.error(f"Counter file write error: {e}")
        return count

    counter = get_next_counter()

    # 대나무숲 채널에 메시지 업로드
    try:
        client.chat_postMessage(
            channel=BAMBOO_CHANNEL_ID,
            text=f"*#{counter}번 제보 - {name}*\n\n{message}"
        )
    except Exception as e:
        logger.error(f"메시지 업로드 실패: {e}")


if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
