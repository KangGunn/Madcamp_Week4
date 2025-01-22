import os
from dotenv import load_dotenv
load_dotenv()
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from algorithm import match_teams  # 팀 매칭 알고리즘 가져오기

SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)

# 설문 데이터를 저장할 임시 스토리지
survey_data = {}
users_in_channel = []  # 채널의 모든 구성원 목록


@app.command("/팀원매칭")
def start_match_command(ack, body, client):
    ack()
    
    global users_in_channel
    response = client.conversations_members(channel=body["channel_id"])
    bot_user_id = client.auth_test()["user_id"]  # 봇의 사용자 ID 가져오기

    # 봇 자신을 제외한 멤버 리스트 생성
    users_in_channel = [user for user in response["members"] if user != bot_user_id]

    client.chat_postMessage(
        channel = body["channel_id"],
        text = "팀 빌딩을 시작합니다! 아래 버튼을 클릭해 사전 조사에 참여해주세요.",
        blocks = [
            {
                "type" : "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "설문조사 시작"},
                        "action_id": "open_survey_modal"
                    }
                ]
            }
        ]
    )


@app.action("open_survey_modal")
def open_survey_modal(ack, body, client):
    ack()
    channel_id = body["channel"]["id"]

    client.views_open(
        trigger_id = body["trigger_id"],
        view = {
            "type": "modal",
            "callback_id": "survey_submission",
            "private_metadata": channel_id,  # 채널 ID 저장
            "title": {
                "type": "plain_text",
                "text": "팀 빌딩",
                "emoji": True
            },
            "submit": {
                "type": "plain_text",
                "text": "Submit",
                "emoji": True
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel",
                "emoji": True
            },
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": ":wave: 사전 정보를 알려주시면 꼭 맞는 팀원을 찾아드릴게요. \n\n호불호가 없다면 빈칸으로 제출하세요!",
                        "emoji": True
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "input",
                    "optional": True,
                    "element": {
                        "type": "multi_users_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select users",
                            "emoji": True
                        },
                        "action_id": "preferred_users_select"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "짝이 되고 싶은 팀원",
                        "emoji": True
                    },
                    "block_id": "preferred_teammates"
                },
                {
                    "type": "input",
                    "optional": True,
                    "element": {
                        "type": "multi_users_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select users",
                            "emoji": True
                        },
                        "action_id": "not_preferred_users_select"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "짝이 되고 싶지 않은 팀원",
                        "emoji": True
                    },
                    "block_id": "not_preferred_teammates"
                }
            ]
        }
    )    


@app.view("survey_submission")
def handle_survey_submission(ack, body, client):
    ack()

    # private_metadata에서 채널 ID 가져오기
    channel_id = body["view"]["private_metadata"]

    # 사용자 정보와 설문 데이터 저장
    user_id = body["user"]["id"]
    preferences = body["view"]["state"]["values"]

    # 필드가 비었을 경우 빈 리스트로 설정
    preferred_users = preferences["preferred_teammates"].get("preferred_users_select", {}).get("selected_users", [])
    not_preferred_users = preferences["not_preferred_teammates"].get("not_preferred_users_select", {}).get("selected_users", [])

    survey_data[user_id] = {
        "preferred_users": preferred_users,
        "not_preferred_users": not_preferred_users
    }

    # 제출한 사람과 제출하지 않은 사람 계산
    submitted_users = list(survey_data.keys())
    not_submitted_users = [user for user in users_in_channel if user not in submitted_users]

    # 실시간 상태 업데이트
    if not_submitted_users:
        not_submitted_text = f"제출하지 않은 사람: <@{'>, <@'.join(not_submitted_users)}>"
    else:
        not_submitted_text = "모든 사용자가 설문을 제출했습니다! 🎉"

    client.chat_postMessage(
        channel=channel_id,
        text=f"현재까지 제출 상황:\n\n"
             f"제출한 사람: <@{'>, <@'.join(submitted_users)}>\n"
             f"{not_submitted_text}"
    )

    if not not_submitted_users:
        announce_teams(client, channel_id)


def announce_teams(client, channel_id):
    matched_teams = match_teams(survey_data)

    # 팀 매칭 결과 발표
    team_messages = [f"팀 {i + 1}: <@{team[0]}> & <@{team[1]}>" for i, team in enumerate(matched_teams)]
    client.chat_postMessage(
        channel=channel_id,
        text="📣 *팀 매칭 결과가 발표되었습니다!* 📣\n\n" + "\n".join(team_messages)
    )



if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()