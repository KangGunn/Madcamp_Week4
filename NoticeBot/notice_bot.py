import os
import re
import json
import logging
import requests

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError
from datetime import datetime
from pprint import pprint

load_dotenv()
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")

app = App(token=SLACK_BOT_TOKEN)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NOTICE_DB_ID = os.getenv("NOTICE_DB_ID")

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
}

query_url = f"https://api.notion.com/v1/databases/{NOTICE_DB_ID}/query"
response = requests.post(query_url, headers=headers)
pages = response.json().get("results", [])
# pprint(pages)
page_info = {}
page_tags = {}
for page in pages:
    if page["object"] == "page":
        if page["properties"]["제목"]["title"][0]["text"]["content"]:
            title = page["properties"]["제목"]["title"][0]["text"]["content"].strip()
            id = page["id"]
            tags = []
            for tag in page["properties"]["태그"]["multi_select"]:
                tags.append(tag["name"])

            page_info[title] = id
            page_tags[title] = tags

# pprint(page_info)

@app.command("/수강료_납부_안내")
def tuition_info(ack, body, say):
    ack()
    global page_info, headers
    title = '수강료 납부 안내'
    page_id = page_info[title]

    page_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response = requests.get(page_url, headers=headers)
    blocks = response.json()['results']
    
    page_content = ""
    for block in blocks:
        if block["type"] == 'paragraph':
            texts = block['paragraph']['rich_text']
            if texts:
                for text in texts:
                    page_content += text['plain_text']
                page_content += "\n"
            else:
                page_content += "\n"

    say(text="수강료 납부 안내 내용입니다.",
        blocks=[
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": title
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": page_content
            }
        }
    ])

@app.command("/강연_면담_안내")
def lecture_info(ack, body, say):
    ack()
    global page_info

    def parse_date_from_key(key):
        """
        문자열에서 월과 일을 추출하여 2025년 기준 datetime 객체로 반환.
        예) "1월 10일 / 강연 상세" → datetime(2025, 1, 10)
        """
        match = re.search(r'(\d{1,2})월\s*(\d{1,2})일', key)
        if match:
            month, day = match.groups()
            try:
                return datetime(2025, int(month), int(day))
            except ValueError:
                return None
        return None

    # 리스트에 (datetime, new_key, value) 형태로 담기
    items = []
    for key, value in page_info.items():
        dt = parse_date_from_key(key)
        if dt is None:
            continue  # 날짜 파싱에 실패한 항목은 건너뜀
        if '강연' in key or '면담' in key:
            items.append((dt, key, value))

    # datetime 기준으로 오름차순 정렬
    items_sorted = sorted(items, key=lambda tup: tup[0])

    # 정렬된 순서대로 딕셔너리 생성
    lectures_dict = {new_key: val for dt, new_key, val in items_sorted}

    # 각 key(ex. 1월 2일 강연)에 해당하는 버튼 만들기
    render_message(lectures_dict, say, '강연/면담 안내')

@app.command("/타대생_안내")
def otheruniv_info(ack, body, say):
    ack()
    global page_info

    # 타대생 관련 제목만 필터링
    filtered_page_info = {
        title: id
        for title, id in page_info.items()
        if "타대생" in title
    }

    render_message(filtered_page_info, say, '타대생 안내 사항')

@app.command("/실습_발표_kcloud_안내")
def activity_info(ack, body, say):
    ack()
    global page_info, page_tags

    # 태그에 "실습" 또는 "발표"가 포함된 페이지 필터링
    filtered_page_info = {
        title: page_info[title]
        for title, tags in page_tags.items()
        if "실습" in tags or "발표" in tags
    }

    render_message(filtered_page_info, say, '실습 및 발표 안내 사항 (KCLOUD 포함)')

@app.command("/개강_안내")
def init_info(ack, body, say):
    ack()
    global page_info

    # 특정 제목만 필터링
    target_titles = [
        "참가자 프로필 꾸미기 / Notion 초대",
        "몰입캠프 개강 안내",
        "몰입캠프 사전 OT"
    ]

    filtered_page_info = {
        title: id
        for title, id in page_info.items()
        if title in target_titles
    }

    render_message(filtered_page_info, say, '개강 관련 안내 사항')



def render_message(lectures_dict, say, title):
    """
    lectures_dict의 각 키(예: "1월 10일 강연")와 페이지 ID를 기반으로 
    버튼들을 포함하는 메시지 블록을 생성하여 전송합니다.
    """
    # 첫 번째 블록에 제목 추가
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": title
            }
        }
    ]
    
    # 각 항목마다 버튼 블록 생성
    for label, page_id in lectures_dict.items():
        block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{label}"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "보기"
                },
                "action_id": "open_page",
                # 버튼의 value에 label과 page_id를 구분자("||")로 연결해 전달
                "value": f"{label}||{page_id}"
            }
        }
        blocks.append(block)
    
    say(blocks=blocks, text=title)

@app.action("open_page")
def handle_open_page(ack, body, say):
    """
    사용자가 버튼을 클릭하면, 해당 버튼의 value에 저장된 페이지 ID를 이용하여 페이지를 여는 작업을 수행합니다.
    Notion API로 페이지 블록들을 받아 원본 순서대로 처리하며, 텍스트, 이미지, 북마크, 테이블, 파일 등 다양한 블록 유형을 변환합니다.
    """
    ack()
    # value는 "title||page_id" 형태의 문자열이므로 분리한다.
    value_str = body["actions"][0]["value"]
    try:
        title, page_id = value_str.split("||")
    except ValueError:
        say("잘못된 데이터입니다.")
        return

    page_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response = requests.get(page_url, headers=headers)
    try:
        blocks_data = response.json().get("results", [])
    except Exception:
        say("페이지 내용을 불러오는데 실패했습니다.")
        return

    page_blocks = []
    numbered_list_counter = 1  # 번호 매기기 항목 번호

    # 헬퍼 함수: rich_text 객체들로부터 텍스트 추출
    def extract_text(block, block_type):
        texts = block.get(block_type, {}).get("rich_text", [])
        return " ".join(text.get("plain_text", "") for text in texts)

    for block in blocks_data:
        b_type = block.get("type")
        converted = None

        if b_type in ["paragraph", "heading_1", "heading_2", "heading_3", "callout"]:
            text_content = extract_text(block, b_type)
            if b_type in ["heading_1", "heading_2", "heading_3"]:
                formatted = f"*{text_content}*"
            elif b_type == "callout":
                formatted = f"> {text_content}"
            else:
                formatted = text_content
            if not formatted.strip():
                continue
            converted = {
                "type": "section",
                "text": {"type": "mrkdwn", "text": formatted}
            }
        elif b_type == "image":
            image_data = block.get("image", {})
            if "external" in image_data:
                image_url = image_data["external"].get("url")
            elif "file" in image_data:
                image_url = image_data["file"].get("url")
            else:
                image_url = None
            if image_url:
                converted = {
                    "type": "image",
                    "image_url": image_url,
                    "alt_text": "이미지"
                }
        elif b_type == "bookmark":
            bookmark_url = block.get("bookmark", {}).get("url", "")
            if bookmark_url:
                converted = {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"🔖 [북마크]({bookmark_url})"}
                }
        elif b_type == "table":
            # Notion table 블록은 자체에는 table_rows가 없고, 자식 블록으로 table_row들이 존재합니다.
            # 따라서, 자식 블록을 별도로 요청합니다.
            # print("DEBUG: Processing table block, id:", block.get("id"))
            if block.get("has_children"):
                table_children_url = f"https://api.notion.com/v1/blocks/{block['id']}/children"
                table_response = requests.get(table_children_url, headers=headers)
                try:
                    table_rows = table_response.json().get("results", [])
                except Exception as e:
                    # print("DEBUG: Error fetching table children:", e)
                    table_rows = []
                # print("DEBUG: Fetched table children, count:", len(table_rows))
            else:
                table_rows = []
            
            table_text = ""
            for row in table_rows:
                if row.get("type") == "table_row":
                    cells = row.get("table_row", {}).get("cells", [])
                    # print("DEBUG: Processing table_row, number of cells:", len(cells))
                    row_texts = []
                    for cell in cells:
                        # 각 cell은 rich_text 객체들의 리스트입니다.
                        if isinstance(cell, list):
                            cell_text = " ".join(item.get("plain_text", "") for item in cell)
                        else:
                            cell_text = cell.get("plain_text", "")
                        row_texts.append(cell_text)
                    row_line = " | ".join(row_texts)
                    # print("DEBUG: Processed table row text:", row_line)
                    table_text += row_line + "\n"
            # print("DEBUG: Final table_text:", table_text)
            if not table_text.strip():
                continue
            converted = {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"📋 테이블:\n{table_text}"}
            }
        elif b_type == "numbered_list_item":
            text_content = extract_text(block, b_type)
            if not text_content.strip():
                continue
            converted = {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"{numbered_list_counter}. {text_content}"}
            }
            numbered_list_counter += 1
        elif b_type == "file":
            file_data = block.get("file", {})
            # 파일 블록도 "external" 또는 "file" 하위에 URL이 있을 수 있음
            if "external" in file_data:
                file_url = file_data["external"].get("url")
            elif "file" in file_data:
                file_url = file_data["file"].get("url")
            else:
                file_url = None
            if file_url:
                converted = {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"📁 [파일]({file_url})"}
                }
        else:
            # 그 외의 블록 유형은 무시하거나 필요시 추가 처리
            continue

        if converted:
            # 만약 섹션 블록의 텍스트가 빈 문자열이면 추가하지 않음
            if converted.get("type") == "section":
                text_val = converted.get("text", {}).get("text", "")
                if not text_val.strip():
                    continue
            page_blocks.append(converted)

    # 헤더 블록 추가 (제목이 공백이 아니면)
    if title.strip():
        page_blocks.insert(0, {
            "type": "header",
            "text": {"type": "plain_text", "text": title}
        })

    # 만약 텍스트 섹션이 3000자 초과하면 분할 (이미지 등은 분할 대상 아님)
    final_blocks = []
    for block in page_blocks:
        if block.get("type") == "section" and "text" in block:
            text_val = block["text"].get("text", "")
            if len(text_val) > 3000:
                chunks = [text_val[i:i+3000] for i in range(0, len(text_val), 3000)]
                for chunk in chunks:
                    final_blocks.append({
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": chunk}
                    })
            else:
                final_blocks.append(block)
        else:
            final_blocks.append(block)

    try:
        say(text="노션 내용입니다.", blocks=final_blocks)
    except Exception as e:
        say("메시지를 전송하는 데 실패했습니다.")
        print(f"Error: {e}")

if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()