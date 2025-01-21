import os, json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from ics import Calendar, Event

SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)

channel_id = "C0895MV7P9U"      # '일정 공지' 채널

def send_reminder(event):
    title = event["title"]
    date = datetime.strptime(event["date"], "%Y-%m-%d")

    calendar_url = generate_gcal_deeplink(title, event["date"])  # Deep Link 생성

    app.client.chat_postMessage(
        channel = channel_id,
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📅 *{title}* 일정이 *{date.strftime('%Y년 %m월 %d일')}* 에 예정되어 있습니다!"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": " 캘린더에 추가"
                        },
                        "action_id": "add_to_ical",
                        "value": json.dumps(event)  # JSON 형태로 일정 데이터를 전달
                    },
                                        {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "구글 캘린더에 추가"
                        },
                        "url": calendar_url
                    }
                ]
            }
        ]
    )

def create_ical_event(title, date):
    c = Calendar()
    e = Event()
    e.name = title
    e.begin = date
    c.events.add(e)

    # 파일명에서 '/'를 ','로 변경
    sanitized_title = title.replace("/", ",")

    # iCal 파일 저장 경로 설정
    directory = os.path.join("ScheduleBot", "ical_files")
    os.makedirs(directory, exist_ok=True)  # 디렉토리 생성 (존재하면 무시)
    file_path = os.path.join(directory, f"{sanitized_title}.ics")

    with open(file_path, "w") as f:
        f.writelines(c)

    return file_path

# iCal 버튼 핸들러
@app.action("add_to_ical")
def handle_add_to_ical(ack, body, client):
    ack()
    user_id = body["user"]["id"]
    response = client.conversations_open(users=user_id)
    dm_channel = response["channel"]["id"]

    # 일정 데이터 가져오기
    action_value = body["actions"][0]["value"]  # 버튼 클릭 시 전달된 값
    event = json.loads(action_value)  # JSON 형태로 저장된 일정 데이터

    # iCal 파일 생성
    file_path = create_ical_event(event["title"], event["date"])

    # Slack에 iCal 파일 업로드
    client.files_upload_v2(
        channels=dm_channel,
        file=file_path,
        title=f"{event['title']} 일정"
    )


def generate_gcal_deeplink(title, date):
    """
    Google Calendar Deep Link 생성 함수.
    :param title: 일정 제목
    :param date: 일정 날짜 (YYYY-MM-DD 형식)
    :return: Google Calendar Deep Link URL
    """
    start_time = date.replace("-", "") + "T090000Z"  # 9시 고정 (UTC)
    end_time = date.replace("-", "") + "T100000Z"    # 10시 고정 (UTC)
    return (
        f"https://www.google.com/calendar/render?action=TEMPLATE"
        f"&text={title}"
        f"&dates={start_time}/{end_time}"
        f"&details=Slack에서 생성된 일정입니다."
    )


def start_socket_mode():
    SocketModeHandler(app, SLACK_APP_TOKEN).start()