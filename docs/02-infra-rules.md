# 02-infra-rules.md — 인프라/서버 규칙

## 공통
- 운영 변경 전 백업 (워크플로우 Export, 설정 파일 백업)
- 비밀값은 ENV/설정 파일에만 (로그/코드/문서에 값 금지)
- 다운타임 최소화: 스테이징/검증 후 반영

## n8n 운영
- API로 업로드 후 반드시 에디터 F5 새로고침 (자세한 내용: docs/06)
- 변경 전 Export JSON 백업 필수
- POST(신규) vs PUT(기존 업데이트) 구분
- top-level nodes와 activeVersion.nodes 양쪽 다 수정

## VPS 운영
- VPS 서버 경로: /docker/n8n/
- docker-compose 경로: /docker/n8n/docker-compose.yml
- 컨테이너 재시작: cd /docker/n8n && docker compose restart n8n n8n-worker
- DB 컨테이너: n8n-postgres (DB: n8ndb, user: n8n)

## 배포 절차 (n8n 2.6.4)
1. SCP → docker cp → n8n import:workflow
2. DB workflow_history 노드 갱신 (activeVersionId 기준)
3. workflow_entity active = true
4. docker compose restart
- import 실행 시 자동 deactivate됨 → 반드시 DB에서 active=true 설정

## 배포/롤백
- 배포 전 git commit 필수
- 문제 발생 시: 중단 → diff 확인 → revert/checkout → 원인 파악 → 다른 접근
