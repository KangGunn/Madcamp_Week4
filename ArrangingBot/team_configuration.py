def send_team_configuration_message(client, channel_id, initiator_id):
    """팀 구성 메시지를 전송"""
    client.chat_postMessage(
        channel=channel_id,
        text=f"<@{initiator_id}> 팀원 정보를 입력하세요.",
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "10개 팀의 구성 정보를 입력하세요."}
            },
            *[
                {
                    "type": "input",
                    "block_id": f"team_{i}_input",
                    "element": {
                        "type": "multi_users_select",
                        "action_id": f"team_{i}_members",
                        "placeholder": {"type": "plain_text", "text": "팀원 2명을 선택하세요"},
                        "max_selected_items": 2
                    },
                    "label": {"type": "plain_text", "text": f"팀 {i} 구성"}
                }
                for i in range(1, 5)
            ],
            {
                "type": "actions",
                "block_id": "team_submit",
                "elements": [
                    {
                        "type": "button",
                        "action_id": "submit_teams",
                        "text": {"type": "plain_text", "text": "팀 구성 완료"},
                        "style": "primary"
                    }
                ]
            }
        ]
    )