# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

## Current Status
- 번역(Claude) ✅ / Seedance(kie.ai) ✅ / TTS(kie.ai) ✅ / Creatomate 합성 ✅ / YouTube 업로드 ✅
- 멀티씬 2씬 E2E 파이프라인 전체 성공 (YouTube 업로드까지)
- Worker 20 노드 (YouTube Code 노드: 환경변수 OAuth + native https PUT)

## Goal
웹앱 구축 (Next.js)

## Next Actions
1. [ ] Next.js 웹앱 초기화
2. [ ] mark-uploaded 자동 실행 안 되는 문제 확인 (DB 상태 uploading에 멈춤)
3. [ ] 멀티씬 3개 이상 테스트

## Last Run
커밋: e4fb0b0 feat: Worker 파이프라인 전면 수정 — 렌더링까지 성공
E2E 결과: 2씬 (include_audio true/false 혼합) → Seedance → TTS → Creatomate → YouTube 업로드 성공
테스트 Job: 0a552f9f (uploaded)
YouTube 영상: HeYLrBD3pmo (AO 파이프라인 테스트 2, unlisted)

## Blockers
- 없음

## n8n 워크플로우 ID
- AO Producer: XV5shW265ht59MTD (active)
- AO Worker: FHYohZccExR24Uha (active)

## n8n 크리덴셜 ID
- Postgres: 4W3WKJLsJKa9hVAA
- KieAI (TTS+Image): OipYAEtrzhD1lJmL
- Creatomate API: 7uzM44eLOitv8ubQ
- Claude API: mr2FTmB2pmyvlbWK
- YouTube OAuth2: FHvjDOGBtI0zvyFA

## VPS 환경변수
- KIEAI_API_KEY, CREATOMATE_API_KEY, YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
- N8N_BLOCK_ENV_ACCESS_IN_NODE=false

## n8n 배포 주의사항 (중요)
- n8n 2.6.4 publish 시스템: CLI import는 draft만 업데이트, activeVersionId 미갱신
- 배포 순서: import → DB workflow_history 노드 갱신 → activeVersionId 동기화 → active=true → restart (2회)
- import 실행 시 자동 deactivate됨

## Worker YouTube 업로드 구조
- Code 노드 1개로 통합 (upload-youtube)
- 환경변수로 OAuth token refresh (YT_CLIENT_ID/SECRET/REFRESH_TOKEN)
- Node.js native https 모듈로 바이너리 PUT (this.helpers.httpRequest EPIPE 우회)
- 흐름: token refresh → HEAD(크기) → resumable init → 영상 다운로드 → PUT upload

## Seedance API 제약
- duration: "4" 또는 "8"만 허용
- input_urls: 직접 .jpg/.png URL만 가능 (리다이렉트 URL 불가)
