import os
import re
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError
from slack_sdk import WebClient
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from threading import Timer

# 환경 변수 로드
load_dotenv()
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

# Slack 앱 초기화
app = App(token=SLACK_BOT_TOKEN)
client = WebClient(token=SLACK_BOT_TOKEN)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 전체 채널에 알림 메시지 전송 함수
def fetch_all_channels():
    """
    Slack의 모든 공개 채널 ID를 가져옵니다.
    """
    try:
        response = client.conversations_list(types="public_channel")
        channels = response.get("channels", [])
        return [channel["id"] for channel in channels]
    except SlackApiError as e:
        logger.error(f"Error fetching channels: {e.response['error']}")
        return []

def send_message_to_channels():
    """
    모든 공개 채널에 메시지를 보냅니다.
    """
    channels = fetch_all_channels()
    for channel_id in channels:
        try:
            client.chat_postMessage(
                channel=channel_id,
                text="📢 밥 먹고 합시다~!! :cymbals::cymbals::cymbals:",
            )
            logger.info(f"Message sent to channel {channel_id}")
        except SlackApiError as e:
            logger.error(f"Error sending message to {channel_id}: {e.response['error']}")

# APScheduler를 사용하여 정해진 시간에 메시지를 보내도록 설정 (정오 12시, 오후 6시)
scheduler = BackgroundScheduler()
scheduler.add_job(send_message_to_channels, 'cron', hour=12, minute=0)  # 매일 12:00 전송
scheduler.add_job(send_message_to_channels, 'cron', hour=18, minute=0)  # 매일 18:00 전송
scheduler.start()

# region 메뉴 관련 설정
main_menus = ["종합", "상황별 메뉴", "재료별 메뉴", "나라별 메뉴"]

sub_menus = {
    "종합": ["찌개", "덮/볶음밥", "국", "야식/술안주", "면", "간식", "밑반찬", "특식"],
    "상황별 메뉴": ["브런치", "초스피드", "식이조절", "도시락", "손님대접", "해장", "간식/야식", "영양식"],
    "재료별 메뉴": ["돼지고기", "닭고기", "달걀", "자투리 채소", "찬밥", "라면", "감자/양파", "참치캔"],
    "나라별 메뉴": ["한국", "일본", "중국", "이탈리아", "프랑스", "미국", "중동", "동남아"]
}

final_menus = {
    # 종합 메뉴
    "찌개": ["청국장찌개", "순두부찌개", "고추장찌개", "부대찌개", "김치찌개", "된장찌개", "비지찌개", "전찌개", "동태찌개"],
    "덮/볶음밥": ["제육덮밥", "비빔밥", "오므라이스", "카레덮밥", "김치볶음밥", "오징어덮밥", "짜장밥", "야채 볶음밥", "간장밥"],
    "국": ["육개장", "떡국", "미역국", "콩나물국", "북엇국", "소고기무국", "시래깃국", "된장국", "감잣국"],
    "야식/술안주": ["두부김치", "소시지야채볶음", "골뱅이무침", "닭똥집볶음", "부침개", "튀김", "콘치즈", "순대볶음", "어묵탕"],
    "면": ["잔치국수", "비빔국수", "칼국수", "우동", "볶음우동", "콩국수", "라면", "토마토 스파게티", "크림 스파게티"],
    "간식": ["토스트", "또띠아피자", "떡꼬치", "쿠키/과자", "떡볶이", "호떡", "샌드위치", "시리얼", "팝시클"],
    "밑반찬": ["연근조림", "시금치무침", "감자조림", "감자채 볶음", "진미채 볶음", "콩나물 무침", "콩조림", "장조림", "멸치볶음"],
    "특식": ["갈비찜", "닭볶음탕", "스테이크", "아귀찜", "삼계탕", "수육", "월남쌈", "불고기", "찜닭"],
    # 상황별 메뉴
    "브런치": ["팬케이크", "프렌치토스트", "에그베네딕트", "몬테크리스토", "크로크무슈/마담", "조개스프", "샐러드파스타", "불고기 부리또", "프리타타"],
    "초스피드": ["연어덮밥", "떡국", "만둣국", "김치볶음밥", "오차즈케", "누룽지죽", "계란찜", "오믈렛", "치킨마요덮밥"],
    "식이조절": ["닭가슴살샐러드", "리코타치즈", "양배추스프", "바나나쉐이크", "해독주스", "단호박스프", "토마토 달걀볶음", "두부스테이크", "곤약국수"],
    "도시락": ["김밥", "바게트버거", "볶음밥", "밥버거", "유부초밥", "스팸무스비", "캘리포니아롤", "샌드위치", "오니기리"],
    "손님대접": ["깐풍만두", "찜닭", "칠리새우", "투움바 파스타", "잡채", "갈비찜", "닭가슴살냉채", "라자냐", "월남쌈"],
    "해장": ["대파라면", "콩나물해장국", "홍합탕", "김치 콩나물죽", "토마토 주스", "굴국밥", "순두부찌개", "북엇국", "오징어무국"],
    "간식/야식": ["토스트", "샌드위치", "시리얼", "또띠아 피자", "팝시클", "떡꼬치", "떡볶이", "쿠키", "호떡"],
    "영양식": ["전복죽", "삼계탕", "닭죽", "추어탕", "장어구이", "더덕구이", "낙지연포탕", "훈제오리 부추무침", "갈비탕"],
    # 재료별 메뉴
    "감자/양파": ["감자채 볶음", "감자고추장찌개", "감자스프", "포테이토 피자", "감자조림", "감자/양파튀김", "감자국", "야채죽", "으깬감자 샐러드"],
    "참치캔": ["참치 비빔밥", "참치김밥", "참치쌈장", "참치볶음밥", "야채참치죽", "참치 김치전", "고추장 참치찌개", "참치마요덮밥", "밥버거"],
    "돼지고기": ["수육", "갈비찜", "동파육", "김치찜", "제육볶음", "두루치기", "탕수육", "목살 스테이크", "불고기"],
    "닭고기": ["닭죽", "닭볶음탕", "찜닭", "치킨까스", "닭강정", "삼계탕", "닭갈비", "치킨마요덮밥", "깐풍기"],
    "달걀": ["계란찜", "계란말이", "오믈렛", "감동란", "계란 장조림", "계란푸딩", "계란빵", "스카치 에그", "스터프드 에그"],
    "찬밥": ["누룽지", "볶음밥", "밥전", "주먹밥", "김치밥 말아먹기", "죽", "리소토", "크로켓", "주먹밥"],
    "라면": ["토마토 냉라면", "짜파구리", "냉채라면", "김치버터라면", "대파라면", "백종원 볶음라면", "골뱅이 비빔면", "라볶이", "크림치즈 라면"],
    "자투리 채소": ["볶음밥", "프리타타", "비빔밥", "잡채", "소시지 야채볶음", "볶음우동", "채소전", "야채볶음", "그라탕"],
    # 나라별 메뉴
    "한국": ["된장찌개", "비빔밥", "칼국수", "불고기", "떡볶이", "제육볶음", "해물파전", "김치", "쌈밥"],
    "일본": ["규동", "우동", "미소시루", "찜닭", "감츠동", "오니기리", "라멘", "오코노미야키", "하이라이스"],
    "중국": ["깐풍기", "볶음면", "동파육", "짜장면", "짬뽕", "마파두부", "탕수육", "토마토달걀볶음", "고추잡채"],
    "이탈리아": ["라자냐", "그라탕", "뇨키", "스파게티", "나폴리 피자", "리소토", "페투치니 알프레도", "프리타타", "파니니"],
    "프랑스": ["끼슈", "마카롱", "뵈프 부르기뇽", "프렌치토스트", "부야베스", "라타투이", "코코뱅", "크로크무슈/마담", "뱅쇼"],
    "미국": ["각종 햄버거", "각종 핫도그", "클램 차우더", "바비큐", "후라이드 치킨", "맥앤치즈", "잠발라야", "미트로프", "에그 베네딕트"],
    "중동": ["케밥", "허머스 (후무스)", "팔라펠", "무사카", "피타", "쿠스쿠스 (중동식 파스타)", "삭슈카 (에그인쉘)", "페투쉬", "필라프"],
    "동남아": ["팟타이", "카오팟", "나시고랭", "파인애플 볶음밥", "쌀국수", "연유라떼", "반미 (바게트 샌드위치)", "짜조", "분짜"]
}
# endregion

@app.command("/뭐먹지")
def what_to_eat(ack, body, say):
    ack()

    blocks = []
    # 상위 메뉴 헤더 추가
    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": ":cheese_wedge::meat_on_bone::bacon::hamburger::pizza::hotdog::taco::burrito::rice_ball::sushi::pancakes::waffle::ice_cream::cake::candy:"
        }
    })

    # 상위 메뉴 버튼 생성
    for label in main_menus:
        block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{label}*"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "보기"
                },
                "action_id": "show_sub_menu",
                "value": label  # 클릭 시 해당 상위 메뉴 이름 전달
            }
        }
        blocks.append(block)

    # 응답 메시지 전송
    say(
        text="상위 메뉴 보기",
        blocks=blocks
    )

@app.action("show_sub_menu")
def handle_sub_menu(ack, body, say):
    ack()
    menu = body["actions"][0]["value"]  # 클릭된 상위 메뉴 이름
    sub_menu_items = sub_menus.get(menu, [])
    blocks = []

    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": ":cheese_wedge::meat_on_bone::bacon::hamburger::pizza::hotdog::taco::burrito::rice_ball::sushi::pancakes::waffle::ice_cream::cake::candy:"
        }
    })

    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f"{menu} 메뉴의 하위 항목"
        }
    })

    # 하위 메뉴 버튼 생성
    for item in sub_menu_items:
        block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{item}"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "보기"
                },
                "action_id": "show_final_menu",
                "value": item  # 클릭 시 해당 하위 메뉴 이름 전달
            }
        }
        blocks.append(block)

    say(
        text=f"{menu} 하위 메뉴 보기",
        blocks=blocks
    )

@app.action("show_final_menu")
def handle_final_menu(ack, body, say):
    ack()
    menu = body["actions"][0]["value"]  # 클릭된 하위 메뉴 이름
    final_items = final_menus.get(menu, [])
    blocks = []

    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": ":cheese_wedge::meat_on_bone::bacon::hamburger::pizza::hotdog::taco::burrito::rice_ball::sushi::pancakes::waffle::ice_cream::cake::candy:"
        }
    })

    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f"{menu}의 세부 항목"
        }
    })

    # 세부 항목 나열 (버튼 없음)
    for item in final_items:
        block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"- {item}"
            }
        }
        blocks.append(block)

    say(
        text=f"{menu} 세부 항목 보기",
        blocks=blocks
    )

# ------------------ 투표로 스크럼 시간 결정 ------------------
# 각 채널의 투표 데이터를 저장하는 딕셔너리
# key: channel_id, value: 해당 채널의 투표 데이터 (question, options, votes, allow_add, anonymous, message_ts)
vote_data_by_channel = {}

@app.command("/메뉴_투표")
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
                "title": {"type": "plain_text", "text": "메뉴 투표"},
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
            "question": f"메뉴 투표(종료 시각: {end_time_input})",
            "options": options,
            "votes": {},
            "allow_add": allow_add,
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

if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
