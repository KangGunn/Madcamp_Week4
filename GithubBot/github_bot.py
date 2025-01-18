import os
from dotenv import load_dotenv
load_dotenv()
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)

# client = WebClient(token=SLACK_BOT_TOKEN)

channel_id = "C089G7VKG5P"      # '튜토리얼' 채널

@app.command("/conv-commit")
def conv_commit(ack):
    ack("Github 커밋 메세지 제목 컨벤션 : \'[TAG]: [영어는 명령형, 한국어는 명사형 문장] \' ")

@app.command("/template")
def conv_issue(ack):
  blocks = [
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "템플릿(Template)이란?",
				"emoji": True
			}
		},
		{
			"type": "rich_text",
			"elements": [
				{
					"type": "rich_text_section",
					"elements": [
						{
							"type": "text",
							"text": "Github에선 "
						},
						{
							"type": "text",
							"text": "issue",
							"style": {
								"code": True
							}
						},
						{
							"type": "text",
							"text": ", "
						},
						{
							"type": "text",
							"text": "P",
							"style": {
								"bold": True,
								"code": True
							}
						},
						{
							"type": "text",
							"text": "ull ",
							"style": {
								"code": True
							}
						},
						{
							"type": "text",
							"text": "R",
							"style": {
								"bold": True,
								"code": True
							}
						},
						{
							"type": "text",
							"text": "equest",
							"style": {
								"code": True
							}
						},
						{
							"type": "text",
							"text": " 을 사용자들의 필요에 맞게 구조화된 양식으로 작성할 수 있도록 템플릿 기능을 제공합니다.\n이 템플릿을 커스터마이징함으로써 작업에 필요한 내용만을 모아 담고, 능률 향상에도 기여할 수 있습니다!"
						}
					]
				}
			]
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*:memo: 템플릿 지정 방법*"
			}
		},
		{
			"type": "context",
			"elements": [
				{
					"type": "plain_text",
					"text": "<Issue>",
					"emoji": True
				}
			]
		},
		{
			"type": "rich_text",
			"elements": [
				{
					"type": "rich_text_quote",
					"elements": [
						{
							"type": "text",
							"text": "Github 에서 직접 생성하기",
							"style": {
								"bold": True
							}
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "ordered",
					"indent": 0,
					"border": 0,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "리포지토리",
									"style": {
										"code": True
									}
								},
								{
									"type": "text",
									"text": " 접속 > 상단바에서 "
								},
								{
									"type": "text",
									"text": "Settings",
									"style": {
										"code": True
									}
								},
								{
									"type": "text",
									"text": " 메뉴 클릭"
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "Features",
									"style": {
										"code": True
									}
								},
								{
									"type": "text",
									"text": " 섹션에서 초록색 "
								},
								{
									"type": "text",
									"text": "Set up templates",
									"style": {
										"code": True
									}
								},
								{
									"type": "text",
									"text": " 버튼 클릭"
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "Add templates",
									"style": {
										"code": True
									}
								},
								{
									"type": "text",
									"text": " 드롭다운 버튼 클릭 > "
								},
								{
									"type": "text",
									"text": "Custom template",
									"style": {
										"code": True
									}
								},
								{
									"type": "text",
									"text": " 클릭"
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "연필 아이콘",
									"style": {
										"code": True
									}
								},
								{
									"type": "text",
									"text": " 버튼 클릭해 markdown(.md) 파일 수정"
								}
							]
						}
					]
				},
				{
					"type": "rich_text_section",
					"elements": [
						{
							"type": "text",
							"text": "\n"
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "bullet",
					"indent": 0,
					"border": 0,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "Pros: "
								}
							]
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "bullet",
					"indent": 1,
					"border": 0,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "작성이 간단하다."
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "link",
									"url": "https://commonmark.org/help/",
									"text": "markdown 문법"
								},
								{
									"type": "text",
									"text": "을 알면 더욱 잘 작성할 수 있다."
								}
							]
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "bullet",
					"indent": 0,
					"border": 0,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "Cons:"
								}
							]
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "bullet",
					"indent": 1,
					"border": 0,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "2번 방법에 비해 설정 과정이 복잡하다."
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "yml 파일에 비해 UI가 투박하다."
								}
							]
						}
					]
				}
			]
		},
		{
			"type": "image",
			"title": {
				"type": "plain_text",
				"text": "md 타입 이슈 템플릿 적용 예시",
				"emoji": True
			},
			"image_url": "https://raw.githubusercontent.com/KangGunn/Madcamp_Week4/refs/heads/2-feat-githubbot/images/yml.png",
			"alt_text": "md templates"
		},
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": "  ",
				"emoji": True
			}
		},
		{
			"type": "rich_text",
			"elements": [
				{
					"type": "rich_text_quote",
					"elements": [
						{
							"type": "text",
							"text": "yml 파일 작성 후 커밋하기",
							"style": {
								"bold": True
							}
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "ordered",
					"indent": 0,
					"border": 0,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "개발 중인 폴더의 최상단 디렉토리에 "
								},
								{
									"type": "text",
									"text": ".github/ISSUE_TEMPLATE",
									"style": {
										"code": True
									}
								},
								{
									"type": "text",
									"text": " 폴더 생성"
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "폴더 내부에 "
								},
								{
									"type": "text",
									"text": "(제목).yml",
									"style": {
										"code": True
									}
								},
								{
									"type": "text",
									"text": " 파일 생성해 작성"
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "Main",
									"style": {
										"code": True
									}
								},
								{
									"type": "text",
									"text": " 리포지토리에 커밋"
								}
							]
						}
					]
				},
				{
					"type": "rich_text_section",
					"elements": [
						{
							"type": "text",
							"text": "\n"
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "bullet",
					"indent": 0,
					"border": 0,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "Pros: "
								}
							]
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "bullet",
					"indent": 1,
					"border": 0,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "1번 방법보다 UI를 자유롭게 커스텀할 수 있다."
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "설정 방법이 간단하다."
								}
							]
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "bullet",
					"indent": 0,
					"border": 0,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "Cons:"
								}
							]
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "bullet",
					"indent": 1,
					"border": 0,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "1번 방법처럼 작성하며 미리보기를 확인할 수 없다."
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "link",
									"url": "https://docs.github.com/ko/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-githubs-form-schema",
									"text": "yml 요소"
								},
								{
									"type": "text",
									"text": "를 파악해야 한다."
								}
							]
						}
					]
				}
			]
		},
		{
			"type": "image",
			"title": {
				"type": "plain_text",
				"text": "yml 타입 이슈 템플릿 적용 예시",
				"emoji": True
			},
			"image_url": "https://raw.githubusercontent.com/KangGunn/Madcamp_Week4/refs/heads/2-feat-githubbot/images/md.png",
			"alt_text": "yml template"
		},
		{
			"type": "divider"
		},
		{
			"type": "context",
			"elements": [
				{
					"type": "plain_text",
					"text": "<PR>",
					"emoji": True
				}
			]
		},
		{
			"type": "rich_text",
			"elements": [
				{
					"type": "rich_text_quote",
					"elements": [
						{
							"type": "text",
							"text": "PR 템플릿 전용 md 파일 작성 후 커밋하기",
							"style": {
								"bold": True
							}
						}
					]
				},
				{
					"type": "rich_text_section",
					"elements": [
						{
							"type": "text",
							"text": "PR 템플릿은 markdown 형식만 지원하며, Github에서 작성할 수 없습니다.",
							"style": {
								"italic": True
							}
						},
						{
							"type": "text",
							"text": "\n\n"
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "ordered",
					"indent": 0,
					"border": 0,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "개발 중인 폴더의 최상단 디렉토리에 "
								},
								{
									"type": "text",
									"text": ".github/pull_request_template.md",
									"style": {
										"code": True
									}
								},
								{
									"type": "text",
									"text": "파일 생성해 작성"
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "Main",
									"style": {
										"code": True
									}
								},
								{
									"type": "text",
									"text": " 리포지토리에 커밋"
								}
							]
						}
					]
				}
			]
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*:octopus: GithubBot이 작성한 yml 파일을 공유드릴게요.*"
			}
		},
		{
			"type": "rich_text",
			"elements": [
				{
					"type": "rich_text_section",
					"elements": [
						{
							"type": "text",
							"text": "아래 버튼을 클릭해 폴더를 다운받은 후, 로컬 리포지토리(현재 개발 코드가 있는, git init을 했던 폴더) 속에 추가해주세요!\n"
						},
						{
							"type": "text",
							"text": "main",
							"style": {
								"code": True
							}
						},
						{
							"type": "text",
							"text": " 브랜치에 커밋하는 순간 바로 적용됩니다 :)"
						}
					]
				}
			]
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Issue Template 다운로드",
						"emoji": True
					},
					"value": "click_me_123",
					"action_id": "download_issue"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "PR Template 다운로드",
						"emoji": True
					},
					"value": "click_me_123",
					"action_id": "download_pr"
				}
			]
		}
	]
  ack(blocks=blocks)

issue_template_path = os.path.abspath("./templates/issue_template.yml")
pr_template_path = os.path.abspath("./templates/pull_request_template.md")

@app.action("download_issue")
def handle_download_issue(ack, body, client):
    ack()
    user_id = body["user"]["id"]
    response = client.conversations_open(users=user_id)
    dm_channel = response["channel"]["id"]

    client.files_upload_v2(
        channels=dm_channel, # 비밀톡
        file=issue_template_path,
        title="이슈 템플릿",
        initial_comment="프로젝트 루트 디렉토리에 붙여넣으세요!"
    )

@app.action("download_pr")
def handle_download_pr(ack, body, client):
    ack()
    user_id = body["user"]["id"]
    response = client.conversations_open(users=user_id)
    dm_channel = response["channel"]["id"]

    client.files_upload_v2(
        channels=dm_channel, # 비밀톡
        file=pr_template_path,
        title="PR 템플릿",
        initial_comment="프로젝트 루트 디렉토리에 붙여넣으세요!"
    )

@app.event("message")
def say_hi(body, say):
    # 사용자 ID 가져오기
    user_id = body.get("event", {}).get("user", "unknown user")
    text = body.get("event", {}).get("text", "")
    bot_id = app.client.auth_test()["user_id"]
    
    # 봇이 스스로의 메시지에 반응하지 않도록 필터링
    if user_id != "USLACKBOT" and f"<@{bot_id}>" not in text:
        say(f"<@{user_id}> 님, 오늘도 힘내세요!")

@app.event("app_mention")
def mention_test(say):
    say("왜여")

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()