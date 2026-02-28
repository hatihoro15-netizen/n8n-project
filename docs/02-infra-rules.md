# 인프라/서버 규칙

## 서버 접속 정보
| 항목 | 값 | 비고 |
|------|-----|------|
| n8n URL | https://n8n.srv1345711.hstgr.cloud | 자체 호스팅 |
| NCA 서버 | 환경변수로 관리 | 하드코딩 금지 |
| SSL | curl -sk 사용 | SSL 인증서 문제 대응 |

## n8n API 규칙
- GET /credentials 미지원 (POST/DELETE만 가능)
- 워크플로우 업로드 후 반드시 에디터 F5 새로고침
- API 업로드와 에디터 저장 충돌 주의

## 크레덴셜 관리
| 이름 | 타입 | 용도 |
|------|------|------|
| Google Gemini(PaLM) Api | googlePalmApi | AI 콘텐츠 생성 |
| Google Sheets | googleSheetsOAuth2Api | 시트 기록/업데이트 |
| Kie.ai API Key | httpHeaderAuth | 이미지/영상 생성 |

## 배포 절차
1. 로컬에서 워크플로우 JSON 수정/생성
2. n8n API로 업로드
3. **반드시 n8n 에디터에서 F5 새로고침**
4. 에디터에서 변경사항 반영 확인
5. 테스트 실행
6. 정상 동작 확인 후 활성화

## 금지 사항
- 서버 IP 하드코딩 (환경변수/설정 파일 사용)
- 서버 임의 비활성화/재시작
- 크레덴셜 코드 내 하드코딩
- 운영 중 워크플로우 직접 수정 (반드시 로컬에서 수정 후 배포)
