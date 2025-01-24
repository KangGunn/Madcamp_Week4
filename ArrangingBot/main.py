import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from team_configuration import send_team_configuration_message
from seat_announcement import *
from seat_allocation import allocate_seats

# 환경 변수 로드
load_dotenv()

SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)

# 글로벌 변수
teams = {}  # 팀 정보
bets = {f"seat_{i}": [] for i in range(1, 11)}  # 자리별 배팅 정보
participants = []
initiator_id = None


@app.event("app_mention")
def start_seat_allocation(event, say, client):
    """봇 언급 시 팀 구성 메시지 표시"""
    global participants, initiator_id

    # 봇 언급자 정보
    channel_id = event["channel"]
    initiator_id = event["user"]

    # 채널 멤버 수집 (봇 제외)
    all_members = client.conversations_members(channel=channel_id)["members"]
    participants = [
        user for user in all_members if not client.users_info(user=user)["user"]["is_bot"]
    ]

    if len(participants) != 4:
        say("⚠️ 채널 내 사용자 수가 20명이 아닙니다. 게임은 20명이 있어야 가능합니다.")
        return

    # 팀 구성 메시지 전송
    send_team_configuration_message(client, channel_id, initiator_id)


@app.action("submit_teams")
def handle_start_betting_submission(ack, body, client, say):
    ack()
    global teams

    try:
        # 팀 구성 데이터 추출
        raw_team_data = body["state"]["values"]
        teams = {}

        for block_id, block_data in raw_team_data.items():
            # 각 팀의 데이터를 처리
            action_id = list(block_data.keys())[0]
            selected_users = block_data[action_id]["selected_users"]

            # 팀원이 2명일 때만 처리
            if len(selected_users) == 2:
                user1, user2 = selected_users
                teams[user1] = user2
                teams[user2] = user1

        # 디버깅 출력
        print(f"Teams: {teams}")

        # 배팅 시작
        channel_id = body["container"]["channel_id"]
        say(f"🎲 팀 구성이 완료되었습니다. 배팅을 시작합니다!")
        start_betting_phase(client, channel_id)

    except KeyError as e:
        say(f"⚠️ 팀 구성 중 오류가 발생했습니다: {str(e)}")
        print(f"⚠️ KeyError: {e}")
    except Exception as e:
        say(f"⚠️ 팀 구성 중 예상치 못한 오류가 발생했습니다: {str(e)}")
        print(f"⚠️ Exception: {e}")


def start_betting_phase(client, channel_id):
    """
    봇 호출 채널에 배팅 모달을 여는 버튼을 보냅니다.
    Args:
        client: Slack Web API 클라이언트.
        channel_id: 봇이 호출된 채널 ID.
    """
    try:
        # 채널에 메시지 전송
        client.chat_postMessage(
            channel=channel_id,
            text="🎲 배팅을 시작합니다! 각 자리에 응모권을 배팅하세요.",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "아래 버튼을 클릭하여 자리 배팅 모달을 엽니다."
                    },
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "배팅 시작"},
                            "style": "primary",
                            "action_id": "open_betting_modal",  # 버튼 클릭 시 모달 열기
                        }
                    ],
                },
            ],
        )
    except Exception as e:
        print(f"⚠️ 배팅 버튼 전송 중 오류 발생: {e}")

@app.action("open_betting_modal")
def handle_open_betting_modal(ack, body, client):
    """배팅 모달 열기"""
    ack()
    trigger_id = body["trigger_id"]
    channel_id = body["channel"]["id"]  # 채널 ID 추출
    open_betting_modal(client, trigger_id, channel_id)


def open_betting_modal(client, trigger_id, channel_id):
    """
    자리 배팅을 위한 모달을 띄웁니다.
    Args:
        client: Slack Web API 클라이언트.
        trigger_id: 트리거 ID (이벤트로부터 전달됨).
        channel_id: 현재 채널 ID.
    """
    client.views_open(
        trigger_id=trigger_id,
        view={
            "type": "modal",
            "callback_id": "submit_betting",
            "private_metadata": channel_id,  # 채널 ID 저장
            "title": {"type": "plain_text", "text": "자리 배팅"},
            "submit": {"type": "plain_text", "text": "제출"},  # 제출 버튼 추가
            "close": {"type": "plain_text", "text": "취소"},   # 닫기 버튼 추가
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "각 자리에 배팅할 응모권 수를 입력하세요. (총 5장까지 가능)"
                    },
                },
                *[
                    {
                        "type": "input",
                        "block_id": f"seat_{i}_betting",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "bet_input",
                            "placeholder": {"type": "plain_text", "text": f"자리 {i}번에 배팅할 수를 입력"}
                        },
                        "label": {"type": "plain_text", "text": f"자리 {i}번"},
                    }
                    for i in range(1, 11)
                ],
            ],
        }
    )


@app.view("submit_betting")
def handle_bet_submission(ack, body, client):
    """배팅 데이터 처리 후 자리 배정 및 제출 상황 업데이트"""
    global bets, participants
    print(f"Initial bets: {bets}")

    # 모달 닫기
    ack()

    # 제출된 입력 데이터 가져오기
    submitted_data = body["view"]["state"]["values"]
    user_id = body["user"]["id"]
    channel_id = body["view"]["private_metadata"]  # 모달 생성 시 저장한 채널 ID

    # 제출된 사용자 저장
    bets["submitted_users"] = bets.get("submitted_users", [])
    if user_id not in bets["submitted_users"]:
        bets["submitted_users"].append(user_id)

    # 배팅 정보 업데이트
    for block_id, block_data in submitted_data.items():
        normalized_block_id = block_id.replace("_betting", "")  # '_betting' 접미사 제거
        bet_value = block_data["bet_input"]["value"]
        if not bet_value:  # 입력이 없으면 기본값 0으로 처리
            bet_value = "0"
        bets[normalized_block_id].extend([user_id] * int(bet_value))

    print(f"Updated bets: {bets}")

    # 제출하지 않은 사용자 계산
    not_submitted_users = [user for user in participants if user not in bets["submitted_users"]]

    # 상태 메시지 생성 및 전송
    if not_submitted_users:
        not_submitted_text = f"⚠️ 제출하지 않은 사용자: <@{'>, <@'.join(not_submitted_users)}>"
        client.chat_postMessage(channel=channel_id, text=not_submitted_text)
    else:
        client.chat_postMessage(
            channel=channel_id,
            text="🎉 모든 사용자가 배팅을 제출했습니다! 자리 배정을 시작합니다."
        )
        try:
            # 자리 배정 및 발표
            seats_result = allocate_seats(teams, bets)
            # announce_seats_progressively(client, seats_result, channel_id)
            announce_all_seats(client, seats_result, channel_id)
        except Exception as e:
            client.chat_postMessage(
                channel=channel_id,
                text=f"⚠️ 자리 배정 중 문제가 발생했습니다: {str(e)}"
            )

@app.event("message")
def handle_message_event(event, say):
    """두구 이벤트 처리"""
    handle_dugudugu_event(event, say)

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()