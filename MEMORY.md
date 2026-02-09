# N8N YouTube 자동화 프로젝트

## 프로젝트 개요
- 4개 YouTube 채널 (루믹스 솔루션, 온카스터디, 슬롯, 쇼츠 전용) 완전 자동 영상 생성 시스템
- n8n 자체 호스팅: https://n8n.srv1345711.hstgr.cloud
- 상세 내용: [n8n_project.md](n8n_project.md)

## 현재 진행 상태
- 루믹스 채널: 숏폼 v3 + 롱폼 v1 완성, HTTP Auth 크레덴셜 모두 연결 완료
- **남은 작업**: Google Sheets/Gemini/YouTube OAuth2 크레덴셜 워크플로우 노드에 연결
- 다른 3개 채널 워크플로우 아직 미생성

## 사용자 요청 규칙
- **대화 종료 시 항상 GitHub에 push** (git add . && git commit && git push)
- 저장소: https://github.com/hatihoro15-netizen/n8n-project

## 주요 기술 참고
- n8n API GET /credentials 지원 안됨 (POST/DELETE만 가능)
- Kie.ai 응답 → fal.ai 포맷 변환 필요 (영상 URL 정리 노드)
- curl -sk 사용 (SSL 인증서 문제)
