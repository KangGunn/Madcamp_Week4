import os, json
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


@app.event("app_mention")
def mention_test(event, say):
    message_blocks = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🫴 개발에 처음인 분들을 위한 튜토리얼을 준비했습니다!",
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
                                "text": "듣고 싶으신 설명을 골라 주세요."
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
                            "text": "프론트? 백?",
                            "emoji": True
                        },
                        "value": "click_me_123",
                        "action_id": "fb_button"
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
                            "text": "개발 순서",
                            "emoji": True
                        },
                        "value": "click_me_123",
                        "action_id": "p_button"
                    }
                ]
            }
        ]
    }
    say(blocks=message_blocks["blocks"], text="튜토리얼 안내 메시지")


@app.action("fb_button")
def handle_fb_button_click(ack, body, say):
    ack()
    block = [
		{
			"type": "rich_text",
			"elements": [
				{
					"type": "rich_text_section",
					"elements": [
						{
							"type": "text",
							"text": "통상적으로 개발은 웹 개발, 앱 개발 모두 "
						},
						{
							"type": "text",
							"text": "프론트엔드(Frontend) 파트",
							"style": {
								"bold": True
							}
						},
						{
							"type": "text",
							"text": "와 "
						},
						{
							"type": "text",
							"text": "백엔드(Backend) 파트",
							"style": {
								"bold": True
							}
						},
						{
							"type": "text",
							"text": "로 나누어 진행합니다.\n\n"
						}
					]
				},
				{
					"type": "rich_text_quote",
					"elements": [
						{
							"type": "text",
							"text": "프론트엔드",
							"style": {
								"bold": True
							}
						},
						{
							"type": "text",
							"text": "\n웹 혹은 앱의 앞단(보여지는 부분), 즉 "
						},
						{
							"type": "text",
							"text": "사용자가 직접 보게 되는 화면과 인터페이스(UI)",
							"style": {
								"bold": True
							}
						},
						{
							"type": "text",
							"text": "를 개발합니다.\n사용자의 입력을 받아 처리하거나, 데이터를 시각적으로 표현하는 역할을 합니다.\n주로 사용하는 기술:"
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "bullet",
					"indent": 0,
					"border": 1,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "웹"
								}
							]
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "bullet",
					"indent": 1,
					"border": 1,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "HTML",
									"style": {
										"bold": True
									}
								},
								{
									"type": "text",
									"text": ": 웹 페이지의 구조를 설계"
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "CSS",
									"style": {
										"bold": True
									}
								},
								{
									"type": "text",
									"text": ": 디자인과 레이아웃을 정의"
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "JavaScript",
									"style": {
										"bold": True
									}
								},
								{
									"type": "text",
									"text": ": 동적인 기능을 구현"
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "프레임워크/라이브러리",
									"style": {
										"bold": True
									}
								},
								{
									"type": "text",
									"text": ": React, Vue.js, Angular 등"
								}
							]
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "bullet",
					"indent": 0,
					"border": 1,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "앱"
								}
							]
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "bullet",
					"indent": 1,
					"border": 1,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "네이티브",
									"style": {
										"bold": True
									}
								},
								{
									"type": "text",
									"text": ": Android, iOS "
								},
								{
									"type": "text",
									"text": "플랫폼별로",
									"style": {
										"italic": True
									}
								},
								{
									"type": "text",
									"text": " 제공되는 개발 도구&언어 사용"
								}
							]
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "bullet",
					"indent": 2,
					"border": 1,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "Android",
									"style": {
										"bold": True
									}
								},
								{
									"type": "text",
									"text": ": Android Studio w/{java || Kotlin}"
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "iOS",
									"style": {
										"bold": True
									}
								},
								{
									"type": "text",
									"text": ": Xcode w/Swift"
								}
							]
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "bullet",
					"indent": 1,
					"border": 1,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "크로스 플랫폼",
									"style": {
										"bold": True
									}
								},
								{
									"type": "text",
									"text": ": 하나의 소스 코드로 Android, iOS "
								},
								{
									"type": "text",
									"text": "모두",
									"style": {
										"italic": True
									}
								},
								{
									"type": "text",
									"text": " 개발 가능"
								}
							]
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "bullet",
					"indent": 2,
					"border": 1,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "React Native, Flutter, ..."
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
							"text": "\n\n"
						}
					]
				},
				{
					"type": "rich_text_quote",
					"elements": [
						{
							"type": "text",
							"text": "백엔드",
							"style": {
								"bold": True
							}
						},
						{
							"type": "text",
							"text": "\n"
						},
						{
							"type": "text",
							"text": "프론트엔드에서 요청한 데이터를 처리",
							"style": {
								"bold": True
							}
						},
						{
							"type": "text",
							"text": "하거나, "
						},
						{
							"type": "text",
							"text": "서버와 데이터베이스를 관리",
							"style": {
								"bold": True
							}
						},
						{
							"type": "text",
							"text": "하는 역할을 합니다.\n데이터를 저장, 처리, 전달하며, 보안 및 사용자 인증도 담당합니다.\n주로 사용하는 기술:"
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "bullet",
					"indent": 0,
					"border": 1,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "언어 + 프레임워크 조합"
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
									"text": "Python: Django, FastAPI, Flask, ..."
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "Java: Spring, ..."
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "JavaScript: Node.js, next.js, ..."
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
									"text": "데이터베이스"
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
									"text": "RDBMS: MySQL, PostgreSQL, ..."
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "NoSQL: MongoDB, ..."
								}
							]
						}
					]
				}
			]
		}
	]
    
    say(blocks=block, text="프백설명")

@app.action("p_button")
def handle_p_button_click(ack, body, say):
    ack()
    block=[
		{
			"type": "rich_text",
			"elements": [
				{
					"type": "rich_text_section",
					"elements": [
						{
							"type": "text",
							"text": "주제 선정 -> 기능 명세서 작성 및 와이어프레임 설계 -> API 명세서 및 데이터베이스 E-R Diagram 작성 -> 프론트/백 개발 환경 설정 및 개발 착수 -> 연동 및 테스트 -> 배포\n\n"
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
									"text": "주제 선정(아이디에이션)"
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
									"text": "타겟 사용자와 명확한 핵심 기능 및 사용 목적을 정의합니다."
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "방향성(사용하고 싶은 기술, 플랫폼(웹/앱/게임)을 정하면 선정이 용이합니다!"
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "주 사용 도구: Notion"
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
							"text": "\n2. 기능 명세서 작성 및 와이어프레임 설계\n"
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
									"text": "기능 명세서: 구현해야 할 주요 기능 정리: 기능 설명, 구현해야 할 알고리즘 등"
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "와이어프레임: 각 화면별 구조 설계"
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "주 사용 도구: Figma, Notion"
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
							"text": "\n3. API 명세서 작성 및 데이터베이스 E-R Diagram 설계\n"
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
									"text": "API 명세서: 프론트- 백 통신을 위한 API를 정의합니다."
								}
							]
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "bullet",
					"indent": 2,
					"border": 0,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "e.g. 프론트에서 '마이페이지' 버튼 클릭 시, 클릭한 사용자의 정보를 반환"
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "API명, 설명, 요청 URL 엔드포인트, HTTP 메소드 종류, 요청 데이터 형식, 반환 데이터 형식, 개발 진행 상태"
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "주 사용 도구: Notion, Swagger"
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
									"text": "DB E-R Diagram: 데이터베이스의 논리 구조를 설계합니다."
								}
							]
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "bullet",
					"indent": 2,
					"border": 0,
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "link",
									"url": "http://dbdiagram.io",
									"text": "dbdiagram.io"
								},
								{
									"type": "text",
									"text": ", "
								},
								{
									"type": "link",
									"url": "http://erdcloud.com",
									"text": "erdcloud.com"
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
							"text": "\n4. 프론트/백 개발 환경 설정 및 개발 착수\n"
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
									"text": "버전 관리 및 협업을 위해 Github 레포지토리를 생성하고, 각 팀원의 개인 컴퓨터에 clone합니다."
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "파트별로 프레임워크를 선정해 프로젝트 구조를 생성한 뒤 필요 모듈(의존성)을 설치하고 소스 코드 작성에 착수합니다."
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
							"text": "\n5. 연동 및 테스트\n"
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
									"text": "프론트와 백을 연결해 데이터를 정상적으로 주고받을 수 있는지 테스트합니다."
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "주 사용 도구"
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
									"text": "API 테스트: Swagger, Postman, ..."
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
							"text": "\n6. 배포\n"
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
									"text": "온프레미스: 소유한 컴퓨터에서 프론트 및 백 프로젝트를 Run 하여 가동합니다. 포트포워딩을 하지 않을 시 같은 와이파이를 사용하는 사용자들만 접속 가능합니다. "
								},
								{
									"type": "text",
									"text": "ipconfig",
									"style": {
										"code": True
									}
								},
								{
									"type": "text",
									"text": " 명령을 통해 확인한 ip 주소를 주소창에 입력해 접속할 수 있습니다."
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "클라우드 플랫폼: 클라우드 전문 회사에서 제공하는 컴퓨터를 사용하는 방식입니다."
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
									"text": "AWS, GCP, Naver Cloud Platform, ..."
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
									"text": "로컬에서 개발하던 환경을 통째로 옮기기 위해 Docker를, 서버 환경 운용 자동화를 위해 Kubernetes를 사용하면 편리합니다."
								}
							]
						}
					]
				}
			]
		}
	]


    say(blocks=block, text="과정설명")

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()