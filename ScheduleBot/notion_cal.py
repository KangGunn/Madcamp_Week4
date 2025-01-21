import os
from notion_client import Client
from dotenv import load_dotenv
load_dotenv()

NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# 노션 클라이언트 초기화
notion = Client(auth=NOTION_API_TOKEN)

# 노션 캘린더 데이터 가져오기
def fetch_calendar_items():
    response = notion.databases.query(database_id=NOTION_DATABASE_ID)
    events = []
    for result in response["results"]:
        title = result["properties"]["Name"]["title"][0]["plain_text"]
        date = result["properties"]["Date"]["date"]["start"]        # 2025-01-01
        events.append({"title": title, "date": date})
    return events