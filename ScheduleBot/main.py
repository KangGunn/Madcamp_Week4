# main.py
from cronjob import schedule_notifications, run_scheduler
from schedule_bot import start_socket_mode
from threading import Thread

if __name__ == "__main__":
    # 알림 스케줄 설정
    schedule_notifications()

    # 스케줄러를 별도 스레드로 실행
    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.start()

    # Slack 이벤트 핸들러 실행
    start_socket_mode()