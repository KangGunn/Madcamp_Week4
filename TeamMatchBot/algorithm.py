from random import choice, shuffle

def match_teams(survey_data):
    matched_teams = []
    remaining_users = set(survey_data.keys())  # 아직 매칭되지 않은 사용자들

    # 1. `not_preferred_users`가 1명 이상인 사용자들 매칭
    for user, data in survey_data.items():
        if data["not_preferred_users"]:
            preferred_users = [
                u for u in data["preferred_users"] if u in remaining_users and u != user
            ]
            if preferred_users:
                partner = choice(preferred_users)
            else:
                possible_partners = remaining_users - set(data["not_preferred_users"]) - {user}
                partner = choice(list(possible_partners)) if possible_partners else None
            
            if partner:
                matched_teams.append((user, partner))
                remaining_users -= {user, partner}

    # 2. `preferred_users`로 가장 많이 포함된 사용자 순서대로 매칭
    popularity = {}
    for user, data in survey_data.items():
        for preferred in data["preferred_users"]:
            if preferred in remaining_users:
                popularity[preferred] = popularity.get(preferred, 0) + 1
    
    sorted_by_popularity = sorted(popularity.items(), key=lambda x: x[1], reverse=True)
    for user, _ in sorted_by_popularity:
        if user in remaining_users:
            preferred_users = [
                u for u in survey_data[user]["preferred_users"] if u in remaining_users and u != user
            ]
            if preferred_users:
                partner = choice(preferred_users)
            else:
                partner = choice(list(remaining_users - {user})) if remaining_users - {user} else None
            
            if partner:
                matched_teams.append((user, partner))
                remaining_users -= {user, partner}

    # 3. `preferred_users`가 가장 많은 사용자 순서대로 매칭
    num_preferences = {
        user: len(data["preferred_users"]) for user, data in survey_data.items() if user in remaining_users
    }
    sorted_by_preference_count = sorted(num_preferences.items(), key=lambda x: x[1], reverse=True)
    for user, _ in sorted_by_preference_count:
        if user in remaining_users:
            preferred_users = [
                u for u in survey_data[user]["preferred_users"] if u in remaining_users and u != user
            ]
            if preferred_users:
                partner = choice(preferred_users)
            else:
                partner = choice(list(remaining_users - {user})) if remaining_users - {user} else None
            
            if partner:
                matched_teams.append((user, partner))
                remaining_users -= {user, partner}

    # 4. 나머지 사용자들 랜덤 매칭
    remaining_users = list(remaining_users)
    shuffle(remaining_users)
    while len(remaining_users) >= 2:
        user1 = remaining_users.pop(0)
        user2 = remaining_users.pop(0)
        matched_teams.append((user1, user2))

    return matched_teams

# if __name__ == "__main__":
#     survey_data = {
#         "조성제": {"preferred_users": [], "not_preferred_users": ["강건", "김유림"]},
#         "윤서진": {"preferred_users": ["강건"], "not_preferred_users": []},
#         "강건": {"preferred_users": [], "not_preferred_users": []},
#         "김유림": {"preferred_users": ["강건"], "not_preferred_users": []},
#         "박준호": {"preferred_users": [], "not_preferred_users": []},
#         "안지언": {"preferred_users": [], "not_preferred_users": []},
#     }
#     print(match_teams(survey_data))