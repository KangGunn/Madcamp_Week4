from random import choices

def allocate_seats(teams, bets):
    """
    팀 배정을 수행하고 결과를 딕셔너리 형태로 반환.
    Args:
        teams (dict): 사용자와 팀원 매핑 (예: {"U12345": "U67890", "U67890": "U12345"}).
        bets (dict): 자리별 배팅 정보 (예: {"seat_10": ["U12345", "U67890"], ...}).

    Returns:
        dict: 자리 배정 결과 (예: {"seat_1": ["U12345", "U67890"], "seat_2": [], ...}).
    """
    seats_result = {f"seat_{i}": [] for i in range(1, 11)}  # 초기화
    remaining_teams = set(teams.keys())  # 아직 배정되지 않은 팀 목록

    # 10번 자리부터 시작
    for seat_key in sorted(bets.keys(), reverse=True):  # 딕셔너리의 키를 정렬
        candidates = bets[seat_key]  # 배팅 후보 리스트 가져오기

        if candidates:  # 해당 자리에 배팅한 사람이 있는 경우
            winner = choices(candidates, k=1)[0]  # 랜덤 추첨
            if winner not in teams:  # 팀 정보가 없는 사용자 방어 처리
                print(f"⚠️ {winner}가 teams에 없습니다. 건너뜁니다.")
                continue
            team = {winner, teams[winner]}  # 당첨된 팀 구성
            if team & remaining_teams:  # 팀이 아직 배정되지 않았다면
                seats_result[seat_key] = list(team)  # 자리와 팀 추가
                remaining_teams -= team  # 배정된 팀 제거

    return seats_result