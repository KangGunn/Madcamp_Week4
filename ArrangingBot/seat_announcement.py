from collections import Counter

# 자리 발표 순서 및 상태 저장
# announcement_steps = [
#     {"seats": [3, 8], "announced": False},
#     {"seats": [2, 7], "announced": False},
#     {"seats": [4, 9], "announced": False},
#     {"seats": [5], "announced": False},
#     {"seats": [6], "announced": False},
#     {"seats": [1, 10], "announced": False},
# ]
announcement_steps = [
    {"seats": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "announced": False},
]

current_step = 0
dugudugu_counter = Counter()  # "두구" 카운팅
channel_id = None  # 현재 게임 진행 채널 ID
seats_result = {}  # 자리 배정 결과


def handle_dugudugu_event(event, say):
    """슬랙 메시지에서 '두구' 감지"""
    global current_step

    if "두구" in event.get("text", "").strip() and channel_id == event["channel"]:
        user_id = event["user"]
        dugudugu_counter[user_id] += 1

        # "두구" 카운트가 5 이상이면 다음 자리 발표
        if len(dugudugu_counter.keys()) >= 2:
            announce_next_seats(say)


def announce_next_seats(say):
    """다음 자리를 발표"""
    global current_step, dugudugu_counter

    if current_step >= len(announcement_steps):
        say("🎉 모든 자리 발표가 완료되었습니다! 🎉")
        return

    # 발표할 자리를 가져옴
    step_info = announcement_steps[current_step]
    if not step_info["announced"]:
        step_info["announced"] = True
        seats_to_announce = step_info["seats"]

        # 자리 결과 메시지 생성
        messages = [
            f"자리 {seat}번: {', '.join([f'<@{user}>' for user in seats_result.get(seat, [])])}"
            for seat in seats_to_announce
        ]
        say("🎉 다음 자리 발표입니다! 🎉\n" + "\n".join(messages))

        # 다음 단계로 진행
        current_step += 1
        dugudugu_counter.clear()


def announce_seats_progressively(client, result, channel):
    """자리 배정 결과를 단계적으로 발표"""
    global channel_id, seats_result, current_step, announcement_steps

    # 상태 초기화
    channel_id = channel
    seats_result = result
    current_step = 0
    for step in announcement_steps:
        step["announced"] = False

    # 초기 발표
    announce_next_seats(lambda msg: client.chat_postMessage(channel=channel, text=msg))

def announce_all_seats(client, result, channel):
    """모든 자리 결과를 한 번에 발표"""
    global channel_id, seats_result

    # 상태 초기화
    channel_id = channel
    seats_result = result

    # 모든 자리 발표 메시지 생성
    messages = [
        f"자리 {seat}번: {', '.join([f'<@{user}>' for user in seats_result.get(seat, [])])}"
        for seat in range(1, 11)
    ]
    client.chat_postMessage(channel=channel, text="🎉 자리 결과 발표입니다! 🎉\n" + "\n".join(messages))