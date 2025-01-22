import os
import random
import logging
import time
import json  # JSON 파일 입출력을 위한 모듈

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError
from pprint import pprint

# 환경변수 로드
load_dotenv()
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

app = App(token=SLACK_BOT_TOKEN)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 경주 상태 변수 (참가자 이름과 말의 위치 추적)
participants = {}
horse_positions = {}

# 캐시로 사용할 사용자 DB 파일 경로
USER_DB_FILE = "user_db.json"

def load_user_db():
    """user_db.json 파일을 로드합니다."""
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_user_db(db):
    """user_db.json 파일에 저장합니다."""
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

# API 호출 시 ratelimit 오류 처리: Slack이 추천하는 대기 시간만큼 sleep 후 재시도
def safe_api_call(api_call, max_retries=5, **kwargs):
    retries = 0
    while retries < max_retries:
        try:
            return api_call(**kwargs)
        except SlackApiError as e:
            if e.response.get("error") == "ratelimited":
                retry_after = int(e.response.headers.get("Retry-After", 1))
                logger.warning(f"Rate limited. Sleeping for {retry_after} seconds before retry. (Retry {retries + 1}/{max_retries})")
                time.sleep(retry_after)
                retries += 1
            else:
                logger.error(f"API call error: {e.response.get('error')}")
                raise e
    logger.error("Exceeded maximum retries for API call.")
    return None

# 슬랙에서 사용자 ID로 이름 가져오기 (캐시 적용)
def get_user_name(user_id, client):
    # ID 앞의 @를 제거하여 실제 사용자 ID만 남김
    user_id = user_id.lstrip('@')
    # 캐시(DB 파일)에서 사용자 정보 확인
    db = load_user_db()
    if user_id in db:
        return db[user_id]

    try:
        # 사용자 정보 가져오기 (기존 로직)
        response = client.users_list()
        if response["ok"]:
            # 모든 사용자 정보에서 email과 이름을 비교하여 매칭하는 로직
            for user in response["members"]:
                # 각 사용자의 email 정보 추출
                email = user.get("profile", {}).get("email", "")
                if email:
                    # 이메일의 접두어와 user_id를 비교하여 이름 반환
                    email_prefix = email.split('@')[0]
                    if email_prefix == user_id:
                        real_name = user["real_name"]
                        # 캐시에 저장 (user_id: 한글 이름 형식)
                        db[user_id] = real_name
                        save_user_db(db)
                        return real_name
            # 이메일이 일치하는 사용자가 없으면 None 반환
            logger.error(f"User ID '{user_id}' not found in Slack users list.")
            return None
        else:
            logger.error(f"Slack API Error: {response['error']} - {user_id}")
            return None
    except Exception as e:
        logger.error(f"Error getting user info for {user_id}: {e}")
        return None

# 경주 시작 명령어 처리
@app.command("/경주_시작")
def start_race(ack, body, say):
    ack()

    # 참가자들 이름 입력받기 (사용자 @멘션)
    text = body['text']
    participants_list = text.split(" ")

    if len(participants_list) < 2:
        say("경주에는 최소 2명이 참여해야 합니다.")
        return

    # 참가자 이름을 실제 이름으로 변환
    global participants, horse_positions
    participants = {}
    horse_positions = {}
    name_to_id = {}

    for i, user_id in enumerate(participants_list):
        user_name = get_user_name(user_id, say.client)  # 슬랙에서 실제 이름 가져오기 (캐시 사용)
        if user_name:
            participants[f"Horse {i + 1}"] = user_name
            horse_positions[f"Horse {i + 1}"] = 0
            name_to_id[user_name] = user_id
        else:
            logger.error(f"Failed to get name for user ID: {user_id}")
    
    if not participants:
        say("참가자를 찾을 수 없습니다. 유효한 사용자 ID를 확인하세요.")
        return

    # 참가자 이름의 최대 길이 계산
    max_name_length = max(len(name) for name in participants.values())

    # 경주 시작 메시지 전송
    initial_message = say(
        text="경마를 시작합니다!",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"경주 참가자:\n" + "\n".join([f"- {name}" for name in participants.values()])
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "현재 경주 상황:\n" + "\n".join([f"{name}" for name in participants.values()])
                }
            }
        ]
    )

    # 경주 진행
    for i in range(50):  # n번 업데이트로 경주 진행
        winner = race_update(i, initial_message, say.client, max_name_length, name_to_id)  # client 사용
        if winner is not None:
            break
        time.sleep(0.3)  # 0.3초 간격으로 경주 업데이트

# 경주 상태 업데이트 함수
def race_update(step, initial_message, client, max_len, name_to_id):
    weights = [0.4, 0.3, 0.2, 0.1]
    finishline = 60
    winner = None

    # 각 말의 위치를 업데이트
    for horse in horse_positions:
        move = random.choices([1, 2, 3, 4], weights=weights, k=1)[0]
        horse_positions[horse] += move

    # 경주 상황 텍스트
    updated_text = "현재 경주 상황:\n"
    for horse, position in horse_positions.items():
        offset = max_len - len(participants[horse])
        if position >= finishline and winner is None:
            winner = participants[horse]
            updated_text += f"{'_' * position}{'__' * offset + name_to_id[participants[horse]]}:rapidash::crown:\n"
        else:
            updated_text += f"{'_' * position}{'__' * offset + name_to_id[participants[horse]]}:rapidash:\n"
    
    try:
        # 경주 진행 상황 메시지 업데이트
        client.chat_update(
            channel=initial_message["channel"],
            ts=initial_message["ts"],
            text="경마 진행 상황",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": updated_text
                    }
                }
            ]
        )

        if winner:
            say_text = f"🎉 우승자는 {winner}입니다! 🎉"
            client.chat_postMessage(
                channel=initial_message["channel"],
                text=say_text
            )
        
        return winner

    except Exception as e:
        logger.error(f"Error updating message: {e}")

if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
