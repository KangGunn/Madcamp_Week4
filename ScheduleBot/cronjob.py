# scheduler.py
from datetime import datetime, timedelta
import schedule, time
from schedule_bot import send_reminder
from notion_cal import fetch_calendar_items

# 알림 스케줄링 함수
def schedule_notifications():
    events = fetch_calendar_items()
    for event in events:
        title = event["title"]
        date = datetime.strptime(event["date"], "%Y-%m-%d")

        # rn 4 test
        reminder_now = (date - timedelta(days=4)).replace(hour=22, minute=25, second=0)
        if reminder_now > datetime.now():
            schedule.every().day.at(reminder_now.strftime("%H:%M")).do(send_reminder, event)

        # 전날 오후 8시
        reminder_1 = (date - timedelta(days=1)).replace(hour=20, minute=0, second=0)
        if reminder_1 > datetime.now():
            schedule.every().day.at(reminder_1.strftime("%H:%M")).do(send_reminder, event)

        # 당일 오전 9시
        reminder_2 = date.replace(hour=9, minute=0, second=0)
        if reminder_2 > datetime.now():
            schedule.every().day.at(reminder_2.strftime("%H:%M")).do(send_reminder, event)

# 스케줄러 실행 함수
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)