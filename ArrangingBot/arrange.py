import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from seat_allocation import allocate_seats
from seat_announcement import announce_seats_progressively, handle_dugudugu_event

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv()

SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)

# 데이터 저장소
teams = {}  # 팀 정보
bets = {f"seat_{i}": [] for i in range(1, 11)}  # 자리별 배팅 정보
participants = []
initiator_id = None

@app.event("app_mention")
def start_seat_allocation(event, say, client):
    """봇 언급 시 모달 열기"""
    global participants, initiator_id
    channel_id = event["channel"]
    initiator_id = event["user"]  # 봇 언급자 저장

    # 채널 멤버 가져오기 (봇 제외)
    all_members = client.conversations_members(channel=channel_id)["members"]
    participants = [
        user for user in all_members if client.users_info(user=user)["user"]["is_bot"] is False
    ]

    # 멤버가 정확히 20명이 아니면 종료
    if len(participants) != 20:
        say("⚠️ 채널 내 사용자 수가 20명이 아닙니다. 팀 구성 게임은 20명일 때만 가능합니다.")
        return

    # 모달 열기
    trigger_id = event["trigger_id"]
    client.views_open(
        trigger_id=trigger_id,
        view={
            "type": "modal",
            "callback_id": "start_seat_allocation",
            "title": {"type": "plain_text", "text": "자리 배팅 게임"},
            "submit": {"type": "plain_text", "text": "OK"},
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "20명의 팀원 정보를 제출해주세요!"}
                },
                {
                    "type": "input",
                    "element": {
                        "type": "multi_users_select",
                        "action_id": "team_info",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "팀원 2명을 선택하세요"
                        },
                        "max_selected_items": 2  # 한 번에 2명 선택
                    },
                    "label": {"type": "plain_text", "text": "팀원 선택"}
                }
            ]
        }
    )


@app.view("start_seat_allocation")
def handle_start_seat_allocation(ack, body, client, say):
    """모달 제출 시 팀 정보 저장 및 배팅 시작"""
    ack()
    global teams, bets, initiator_id

    # 제출자가 봇 언급자인지 확인
    user_id = body["user"]["id"]
    if user_id != initiator_id:
        say(f"<@{user_id}>, 모달은 봇을 언급한 사용자만 제출할 수 있습니다!")
        return

    # 팀 정보 저장
    selected_users = body["view"]["state"]["values"]["team_info"]["team_info"]["selected_users"]
    try:
        # 팀원 20명 검증
        if len(selected_users) != 20:
            raise ValueError("팀 구성 정보가 정확하지 않습니다. 20명을 모두 선택해야 합니다.")

        # 팀 정보 생성 (2인 1조)
        teams = {selected_users[i]: selected_users[i + 1] for i in range(0, len(selected_users), 2)}
    except Exception as e:
        say("⚠️ 팀 구성 정보가 잘못되었습니다. 다시 시도해주세요!")
        return

    # 자리 배팅 시작 메시지
    say("🎲 자리 배팅이 시작되었습니다! 모든 사용자는 응모권 5장을 원하는 자리에 배팅할 수 있습니다.")
    for user in participants:
        client.chat_postMessage(
            channel=user,
            text="자리 배팅이 시작되었습니다! 응모권 5장을 원하는 자리에 배팅해주세요.",
            attachments=[
                {
                    "color": "#36a64f",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {"type": "mrkdwn", "text": "1~10번 자리 중 원하는 자리에 응모권을 배팅하세요."}
                        },
                        {
                            "type": "input",
                            "block_id": "bet_input",
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "bet_tickets",
                                "placeholder": {"type": "plain_text", "text": "예: seat_1: 3, seat_2: 2"}
                            },
                            "label": {"type": "plain_text", "text": "응모권 배팅"}
                        }
                    ]
                }
            ]
        )

@app.action("bet_tickets")
def handle_bet_submission(ack, body, client):
    """사용자가 배팅 데이터를 제출하면 저장"""
    ack()
    global bets

    user_id = body["user"]["id"]
    bet_input = body["state"]["values"]["bet_input"]["bet_tickets"]["value"]

    # 배팅 데이터 저장
    user_bets = {f"seat_{i}": 0 for i in range(1, 11)}
    try:
        for bet in bet_input.split(", "):
            seat, count = bet.split(": ")
            if seat not in user_bets:
                raise ValueError(f"잘못된 자리: {seat}")
            count = int(count)
            if count < 0:
                raise ValueError(f"음수 값은 허용되지 않습니다: {count}")
            user_bets[seat] += count

        # 티켓 총합 검증 (5장 제한)
        total_tickets = sum(user_bets.values())
        if total_tickets > 5:
            raise ValueError("⚠️ 한 사용자당 최대 5장의 응모권만 사용할 수 있습니다.")

        # 자리별 응모권 저장
        for seat, count in user_bets.items():
            bets[seat].extend([user_id] * count)

        # 모든 사용자 배팅 완료 확인
        all_done = all(len(bets[seat]) > 0 for seat in bets)
        if all_done:
            seats = allocate_seats(teams, bets)
            announce_seats(client, seats, body["channel"]["id"])
    except Exception as e:
        client.chat_postMessage(
            channel=user_id,
            text=f"⚠️ 배팅 데이터가 잘못되었습니다. {str(e)} 다시 시도해주세요!"
        )


@app.event("message")
def handle_message_event(event, say):
    """두구 이벤트 처리"""
    handle_dugudugu_event(event, say)


def announce_seats(client, seats, channel_id):
    """자리 배치 결과 발표를 단계적으로 진행"""
    announce_seats_progressively(client, seats, channel_id)


if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()