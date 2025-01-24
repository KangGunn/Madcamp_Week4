import os
import re
import json
import logging
from datetime import datetime
from threading import Timer

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.base import JobLookupError  # 스케줄러 작업 제거시 사용

load_dotenv()
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

app = App(token=SLACK_BOT_TOKEN)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# region 스크럼 시간 I/O (채널별 관리)
SCRUM_FILE = "scrum.json"

def load_scrum_data():
    """
    파일에서 채널별 스크럼 시간 데이터를 로드합니다.
    legacy 형식 (예: { "scrum_time": "09:00" })이면 이를 무시하고 빈 딕셔너리를 반환합니다.
    """
    try:
        with open(SCRUM_FILE, "r") as f:
            data = json.load(f)
            # legacy 형식 감지: 최상위에 "scrum_time" 키가 존재하면
            if isinstance(data, dict) and "scrum_time" in data and isinstance(data["scrum_time"], str):
                logger.warning("Legacy scrum.json 형식이 감지되었습니다. 새로운 형식으로 전환합니다. (기존 데이터는 무시됩니다.)")
                return {}
            return data
    except FileNotFoundError:
        return {}

def save_scrum_data(scrum_data):
    """
    채널별 스크럼 시간 데이터를 파일에 저장합니다.
    """
    with open(SCRUM_FILE, "w") as f:
        json.dump(scrum_data, f)

# 전역 변수: 채널별 스크럼 시간 데이터 (예: { "C12345": {"scrum_time": "09:00"}, ... })
scrum_data = load_scrum_data()

# APScheduler 시작
scheduler = BackgroundScheduler()
scheduler.start()

@app.command("/set-scrum-time")
def set_scrum_time(ack, body, say, client):
    """
    /set-scrum-time 명령어 처리: 해당 채널에 스크럼 시간을 설정하고 스케줄러 작업을 등록합니다.
    """
    ack()

    new_scrum_time = body["text"].strip()
    channel_id = body["channel_id"]

    try:
        # 채널별 스크럼 시간 저장
        scrum_data[channel_id] = {"scrum_time": new_scrum_time}
        save_scrum_data(scrum_data)

        # 해당 채널에 대한 알림 스케줄 등록
        schedule_scrum_notification(new_scrum_time, channel_id, client)

        say(f"스크럼 시간이 {new_scrum_time}으로 설정되었습니다.")
    except ValueError as e:
        say(f"스크럼 시간 설정 중 오류가 발생했습니다: {e}")

@app.command("/get-scrum-time")
def get_scrum_time(ack, body, say):
    """
    /get-scrum-time 명령어 처리: 해당 채널의 스크럼 시간을 조회합니다.
    """
    ack()
    channel_id = body["channel_id"]
    channel_data = scrum_data.get(channel_id)
    if channel_data and channel_data.get("scrum_time"):
        say(f"스크럼 시간은 {channel_data['scrum_time']}입니다.")
    else:
        say("스크럼 시간이 아직 설정되지 않았습니다.")

def schedule_scrum_notification(scrum_time, channel_id, client):
    """
    스크럼 알림을 위한 스케줄러 작업을 등록합니다.
    채널별 job id를 사용하여 기존 작업은 제거하고 새로 등록합니다.
    """
    # 알림 오프셋 (0, 30, 60분 전)
    notification_offsets = [0, 30, 60]
    for offset in notification_offsets:
        job_id = f"scrum_alert_{channel_id}_{offset}"
        try:
            scheduler.remove_job(job_id)
        except JobLookupError:
            pass

    try:
        scrum_hour, scrum_minute = map(int, scrum_time.split(":"))
    except Exception as e:
        logger.error(f"스크럼 시간 포맷 오류: {e}")
        return

    for offset in notification_offsets:
        alert_hour = (scrum_hour - (offset // 60)) % 24
        alert_minute = (scrum_minute - (offset % 60)) % 60

        scheduler.add_job(
            send_scrum_notification,
            trigger=CronTrigger(hour=alert_hour, minute=alert_minute),
            args=[offset, scrum_time, channel_id, client],
            id=f"scrum_alert_{channel_id}_{offset}",
            replace_existing=True
        )

def send_scrum_notification(offset, scrum_time, channel_id, client):
    """
    스크럼 알림 메시지를 해당 채널에 전송합니다.
    """
    try:
        if offset == 0:
            message = f"⏰ 스크럼을 시작해주세요! ({scrum_time})"
        else:
            message = f"⏰ 스크럼 시작 {offset}분 전입니다! ({scrum_time})"
        client.chat_postMessage(channel=channel_id, text=message)
    except Exception as e:
        logger.error(f"알림 전송 중 오류 발생: {e}")
# endregion

# ------------------ 투표로 스크럼 시간 결정 ------------------
# 각 채널의 투표 데이터를 저장하는 딕셔너리
# key: channel_id, value: 해당 채널의 투표 데이터 (question, options, votes, allow_add, anonymous, message_ts)
vote_data_by_channel = {}

@app.command("/create-vote")
def create_vote(ack, body, client, logger):
    """
    /create-vote 명령어 처리: 모달을 열어 투표를 생성합니다.
    모달 view의 private_metadata에 채널 아이디를 저장하여 이후에 제출시 채널을 구분합니다.
    """
    ack()
    channel_id = body["channel_id"]

    try:
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "create_vote_modal",
                "private_metadata": channel_id,  # 채널 아이디 전달
                "title": {"type": "plain_text", "text": "스크럼 시간 투표"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "vote_options",
                        "optional": True,
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "options",
                            "placeholder": {"type": "plain_text", "text": "옵션을 쉼표로 구분하여 입력"}
                        },
                        "label": {"type": "plain_text", "text": "투표 옵션"}
                    },
                    {
                        "type": "input",
                        "block_id": "end_time",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "end_time_input",
                            "placeholder": {"type": "plain_text", "text": "24시간 형식으로 투표 종료 시각 입력 (예: 18:00)"}
                        },
                        "label": {"type": "plain_text", "text": "투표 종료 시각"}
                    },
                    {
                        "type": "section",
                        "block_id": "allow_add",
                        "text": {"type": "mrkdwn", "text": "*옵션 추가 허용 여부*"},
                        "accessory": {
                            "type": "checkboxes",
                            "action_id": "allow_add_action",
                            "options": [
                                {
                                    "text": {"type": "plain_text", "text": "옵션 추가 허용"},
                                    "value": "yes"
                                }
                            ]
                        }
                    },
                    {
                        "type": "section",
                        "block_id": "anonymous",
                        "text": {"type": "mrkdwn", "text": "*투표 방식* (무기명 체크 시 무기명)"},
                        "accessory": {
                            "type": "checkboxes",
                            "action_id": "anonymous_action",
                            "options": [
                                {
                                    "text": {"type": "plain_text", "text": "무기명"},
                                    "value": "anonymous"
                                }
                            ]
                        }
                    }
                ],
                "submit": {"type": "plain_text", "text": "생성"}
            }
        )
    except Exception as e:
        logger.error(f"Error opening modal: {e}")

# region 경고 처리용 함수 (모달 내 체크박스 관련)
@app.action("allow_add_action")
def ignore_allow_add_action(ack):
    ack()

@app.action("anonymous_action")
def ignore_anonymous_action(ack):
    ack()
# endregion

@app.view("create_vote_modal")
def handle_create_vote(ack, body, client, logger):
    """
    모달 제출 시 투표 데이터를 채널 별로 저장합니다.
    모달의 private_metadata에서 채널 아이디를 받아 사용합니다.
    """
    global vote_data_by_channel
    ack()
    try:
        channel_id = body["view"]["private_metadata"]
        state = body["view"]["state"]["values"]
        options_input = state["vote_options"]["options"]["value"]
        end_time_input = state["end_time"]["end_time_input"]["value"]

        if not options_input:
            options = []
        else:
            options = [opt.strip() for opt in options_input.split(",") if opt.strip()]

        allow_add_selected = state["allow_add"]["allow_add_action"].get("selected_options", [])
        allow_add = True if allow_add_selected else False

        anonymous_selected = state["anonymous"]["anonymous_action"].get("selected_options", [])
        anonymous = True if anonymous_selected else False

        now = datetime.now()
        try:
            end_time = datetime.strptime(end_time_input, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )
            if end_time < now:
                client.chat_postMessage(
                    channel=channel_id,
                    text=":warning: 입력한 시간이 지났습니다. 현재 시각 이후로 설정해주세요."
                )
                return
        except ValueError as e:
            client.chat_postMessage(
                channel=channel_id,
                text=f":warning: 올바르지 않은 시간 형식입니다: {str(e)}"
            )
            return

        # 각 채널의 투표 데이터를 생성
        vote_data_by_channel[channel_id] = {
            "question": f"스크럼 시간 투표(종료 시각: {end_time_input})",
            "options": options,
            "votes": {},
            "allow_add": allow_add,
            "anonymous": anonymous,
            "channel": channel_id,
            "message_ts": None
        }

        blocks = render_vote_message(channel_id)

        result = client.chat_postMessage(
            channel=channel_id,
            blocks=blocks,
            text="투표가 생성되었습니다!"
        )
        vote_data_by_channel[channel_id]["message_ts"] = result["ts"]

        schedule_vote_end(client, channel_id, end_time)

    except KeyError as e:
        logger.error(f"KeyError while processing modal: {e}")
    except Exception as e:
        logger.error(f"Error processing modal: {e}")

def render_vote_message(channel_id):
    """
    해당 채널의 투표 현황 메시지 블록을 구성합니다.
    기존 투표 버튼들에 더해 빨간 텍스트의 '지금 종료하기' 버튼을 추가합니다.
    """
    vote_data = vote_data_by_channel.get(channel_id)
    if vote_data is None:
        return []

    blocks = []
    blocks.append({
        "type": "header",
        "text": {"type": "plain_text", "text": vote_data["question"]}
    })

    sorted_options = sorted(vote_data["options"], key=lambda x: x)
    summary_lines = []
    for option in sorted_options:
        voters = [uid for uid, opt in vote_data["votes"].items() if opt == option]
        count = len(voters)
        if vote_data["anonymous"]:
            summary_line = f"*{option}*: {count}표"
        else:
            if count == 0:
                summary_line = f"*{option}*: 0표"
            else:
                voter_mentions = ", ".join(f"<@{uid}>" for uid in voters)
                summary_line = f"*{option}*: {count}표 ({voter_mentions})"
        summary_lines.append(summary_line)

    if summary_lines:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": "\n".join(summary_lines)}
        })

    # 옵션별 투표 버튼과 '옵션 추가', 그리고 '지금 종료하기' 버튼 구성
    action_elements = []
    for option in sorted_options:
        action_elements.append({
            "type": "button",
            "text": {"type": "plain_text", "text": option},
            "action_id": f"vote_{option}"
        })
    action_elements.append({
        "type": "button",
        "text": {"type": "plain_text", "text": "옵션 추가"},
        "action_id": "add_option"
    })
    # [신규] 빨간 텍스트의 "지금 종료하기" 버튼 추가 (스타일을 빨강으로 지정)
    action_elements.append({
        "type": "button",
        "text": {"type": "plain_text", "text": "지금 종료하기", "emoji": True},
        "action_id": "end_vote_now",
        "style": "danger"
    })
    blocks.append({
        "type": "actions",
        "elements": action_elements
    })
    return blocks

@app.action(re.compile(r"^vote_.*"))
def handle_vote(ack, body, client, logger):
    """
    투표 버튼 클릭 이벤트: 사용자가 동일 옵션 선택 시 투표 취소, 다르면 변경합니다.
    """
    ack()
    try:
        channel_id = body["channel"]["id"]
        vote_data = vote_data_by_channel.get(channel_id)
        if vote_data is None:
            logger.error(f"채널 {channel_id}에 투표 데이터가 존재하지 않습니다.")
            return

        user_id = body["user"]["id"]
        action_id = body["actions"][0]["action_id"]
        option = action_id.split("_", 1)[1]

        if user_id in vote_data["votes"] and vote_data["votes"][user_id] == option:
            del vote_data["votes"][user_id]
        else:
            vote_data["votes"][user_id] = option

        update_vote_message(client, channel_id)
    except Exception as e:
        logger.error(f"Error processing vote: {e}")

def update_vote_message(client, channel_id):
    """
    해당 채널의 투표 현황 메시지를 업데이트합니다.
    """
    vote_data = vote_data_by_channel.get(channel_id)
    if vote_data is None:
        return
    try:
        client.chat_update(
            channel=channel_id,
            ts=vote_data["message_ts"],
            blocks=render_vote_message(channel_id),
            text="투표가 업데이트되었습니다!"
        )
    except SlackApiError as e:
        logger.error(f"Error updating vote message: {e}")

@app.action("add_option")
def handle_add_option(ack, body, client, logger):
    """
    '옵션 추가' 버튼 클릭 시 모달을 열어 새로운 옵션을 입력받습니다.
    모달 호출 시 private_metadata에 채널 아이디를 포함시킵니다.
    """
    ack()
    try:
        channel_id = body["channel"]["id"]
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "add_option_modal",
                "private_metadata": channel_id,
                "title": {"type": "plain_text", "text": "옵션 추가"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "new_option",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "new_option_input"
                        },
                        "label": {"type": "plain_text", "text": "옵션을 입력하세요."}
                    }
                ],
                "submit": {"type": "plain_text", "text": "추가"}
            }
        )
    except Exception as e:
        logger.error(f"Error opening add option modal: {e}")

@app.view("add_option_modal")
def handle_add_option_submission(ack, body, client, logger):
    """
    모달 제출 시, 해당 채널의 투표 데이터에 새로운 옵션을 추가하고 투표 메시지를 업데이트합니다.
    """
    ack()
    try:
        channel_id = body["view"]["private_metadata"]
        state_values = body["view"]["state"]["values"]
        new_option = state_values["new_option"]["new_option_input"]["value"].strip()

        if not new_option:
            client.chat_postMessage(
                channel=channel_id,
                text=":warning: 옵션이 비어있습니다."
            )
            return

        vote_data = vote_data_by_channel.get(channel_id)
        if vote_data is None:
            client.chat_postMessage(
                channel=channel_id,
                text=":warning: 해당 채널에 진행 중인 투표가 없습니다."
            )
            return

        if new_option in vote_data["options"]:
            client.chat_postMessage(
                channel=channel_id,
                text=":warning: 이미 존재하는 옵션입니다."
            )
            return

        vote_data["options"].append(new_option)
        update_vote_message(client, channel_id)
    except Exception as e:
        logger.error(f"Error processing new option modal: {e}")

def finalize_vote(client, channel_id):
    """
    투표 종료 시, 기존의 schedule_vote_end의 내부 로직을 재활용하여 결과를 발표합니다.
    투표 결과를 계산한 후, 결과 메시지를 해당 채널에 전송하고 해당 투표 데이터를 삭제합니다.
    """
    try:
        vote_data = vote_data_by_channel.get(channel_id)
        if vote_data is None:
            return

        sorted_options = sorted(vote_data["options"], key=lambda x: x)
        result_counts = []
        for option in sorted_options:
            count = sum(1 for u, opt in vote_data["votes"].items() if opt == option)
            result_counts.append((option, count))

        result_counts.sort(key=lambda x: x[1], reverse=True)
        results_text = "\n".join(f"*{opt}*: {cnt}표" for opt, cnt in result_counts)
        final_message = f"투표가 종료되었습니다! 결과는 다음과 같습니다:\n\n{results_text}"
        client.chat_postMessage(channel=channel_id, text=final_message)
        # 투표 종료 후 해당 채널의 투표 데이터 제거
        del vote_data_by_channel[channel_id]
    except Exception as e:
        logger.error(f"Error ending vote: {e}")

def schedule_vote_end(client, channel_id, end_time):
    """
    지정된 시각에 해당 채널의 투표를 종료하는 타이머를 등록합니다.
    """
    now = datetime.now()
    delay = (end_time - now).total_seconds()

    def end_vote():
        finalize_vote(client, channel_id)
    Timer(delay, end_vote).start()

# [신규] "지금 종료하기" 버튼 핸들러
@app.action("end_vote_now")
def handle_end_vote_now(ack, body, client, logger):
    """
    '지금 종료하기' 버튼 클릭 시 해당 채널의 투표를 즉시 종료합니다.
    """
    ack()
    try:
        channel_id = body["channel"]["id"]
        finalize_vote(client, channel_id)
    except Exception as e:
        logger.error(f"Error ending vote immediately: {e}")

# --- 앱 시작 시 저장된 각 채널의 스크럼 시간 재스케줄 ---
for channel_id, data in scrum_data.items():
    if isinstance(data, dict):
        scrum_time = data.get("scrum_time")
        if scrum_time:
            schedule_scrum_notification(scrum_time, channel_id, app.client)
# --- END 재스케줄

if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
