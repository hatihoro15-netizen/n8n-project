# N8N 프로젝트 상세

## 워크플로우 ID
| 이름 | ID | 상태 |
|------|-----|------|
| 루믹스 숏폼 v3 | 9YOHS8N1URWlzGWj | HTTP Auth 연결 완료, Google 크레덴셜 미연결 |
| 루믹스 롱폼 v1 | dsP2aQ1YRyeFRRNA | HTTP Auth 연결 완료, Google 크레덴셜 미연결 |
| 전용 (원본) | tCn0Wjzok_227QHWbSDhq | 기존 |
| 전용 (개선판) | wJEiFv03sCFu4nIB | 기존 |
| 루믹스 솔루션 영상 (기존) | FxDdRAP0sVh-dAfawM8k1 | 기존 |
| 숏폼 v2 (이전버전) | aL1VCjROx8RrGk7X | v3으로 대체됨 |
| 설명형 숏츠 - 온카스터디 | dEtWqwWQPJfwCWiIM0QYd | 활성 (구: 유튜브 광고) |
| 설명형 숏츠 - 사공픽 | LJPISE4aEat5xu7P | 활성 |

## 크레덴셜 ID
| 이름 | ID | 타입 |
|------|-----|------|
| Header Auth account (fal.ai) | R0m2RD0rtE8IKRt6 | httpHeaderAuth |
| Kie.ai | 34ktW72w0p8fCfUQ | httpHeaderAuth |
| Shotstack | 3oEYwvtDnmFeylkp | httpHeaderAuth |
| Pexels | 1vPRgFSX7u4ecIy4 | httpHeaderAuth |
| Google Sheets | CWBUyXUqCU9p5VAg | googleSheetsOAuth2Api |
| Google Gemini | IKP349r08J9Hoz5E | googlePalmApi |
| YouTube | ? | youTubeOAuth2Api - 사용자가 생성함, ID 미확인 |

## API 선택 (사용자 확정)
- 이미지: FLUX 2 Pro ($0.03/장) via fal.ai
- 영상: Kie.ai Kling 2.6 ($0.28/5초) - 숏폼용
- TTS: ElevenLabs via fal.ai
- 업스케일: AuraSR via fal.ai (사용자가 업스케일 유지 요청)
- BGM: Beatoven via fal.ai
- 롱폼: Pexels 스톡영상 사용

## 숏폼 v3 - Google 크레덴셜 필요 노드
| 노드 이름 | 노드 타입 | 필요 크레덴셜 타입 |
|-----------|----------|-------------------|
| AI 주제 생성 | @n8n/n8n-nodes-langchain.googleGemini | googlePalmApi |
| 나레이션 분할 | @n8n/n8n-nodes-langchain.googleGemini | googlePalmApi |
| Gemini Chat Model | @n8n/n8n-nodes-langchain.lmChatGoogleGemini | googlePalmApi |
| 시트 기록 | n8n-nodes-base.googleSheets | googleSheetsOAuth2Api |
| 상태 업데이트 | n8n-nodes-base.googleSheets | googleSheetsOAuth2Api |
| 발행 완료 | n8n-nodes-base.googleSheets | googleSheetsOAuth2Api |
| YouTube 업로드 | n8n-nodes-base.youTube | youTubeOAuth2Api |

## 롱폼 v1 - Google 크레덴셜 필요 노드
| 노드 이름 | 노드 타입 | 필요 크레덴셜 타입 |
|-----------|----------|-------------------|
| AI 대본 생성 | @n8n/n8n-nodes-langchain.googleGemini | googlePalmApi |
| 시트 기록 | n8n-nodes-base.googleSheets | googleSheetsOAuth2Api |
| 상태 업데이트 | n8n-nodes-base.googleSheets | googleSheetsOAuth2Api |
| 발행 완료 | n8n-nodes-base.googleSheets | googleSheetsOAuth2Api |
| YouTube 업로드 | n8n-nodes-base.youTube | youTubeOAuth2Api |

## n8n API 주의사항
- API Key: JWT 토큰 (eyJhbGci...)
- SSL: -k 플래그 필수 (자체호스팅 인증서 문제)
- GET /credentials: 지원 안됨
- PUT /workflows: name, nodes, connections, settings만 포함 (id, createdAt, shared 등 제거)
- settings: executionOrder만 포함 (binaryMode, availableInMCP 제거)

## 프로젝트 파일 위치
- /Users/gimdongseog/n8n-project/ (모든 스크립트 및 JSON)

## 남은 작업
1. Google Sheets/Gemini/YouTube 크레덴셜을 숏폼v3 + 롱폼v1 노드에 연결
2. 테스트 실행
3. 업스케일 on/off 비교 테스트
4. 나머지 3개 채널 워크플로우 생성 (온카스터디, 슬롯, 쇼츠 전용)
