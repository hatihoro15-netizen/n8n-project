# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

## Current Status
- 번역(Claude) ✅ / Seedance(kie.ai) ✅ / TTS(kie.ai) ✅ / Creatomate 합성 ✅ / YouTube 업로드 ✅
- 웹앱 콜백 연동 ✅ (production_id 기반, uploaded/failed 시 POST 콜백)
- Worker 22 노드 (콜백 성공/실패 2개 추가)

## Goal
웹앱 E2E 테스트

## Next Actions
1. [ ] 프론트에서 productionId 포함 요청 → 콜백 수신 E2E 테스트
2. [ ] 멀티씬 3개 이상 테스트

## Last Run
배포: 웹앱 콜백 연동 (Producer production_id 저장 + Worker 콜백 노드 2개)
콜백 URL: https://api-n8n.xn--9g4bn4fm2bl2mb9f.com/api/productions/callback

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
- WEBAPP_CALLBACK_URL=https://api-n8n.xn--9g4bn4fm2bl2mb9f.com
- N8N_BLOCK_ENV_ACCESS_IN_NODE=false

## 웹앱 콜백 구조
- Producer: `productionId` → jobs.production_id 저장
- Worker 성공 콜백 (상태→uploaded 후):
  POST {WEBAPP_CALLBACK_URL}/api/productions/callback
  body: { productionId, status: 'uploaded', youtubeVideoId, youtubeUrl, renderedVideoUrl, jobId }
- Worker 실패 콜백 (재시도/실패 후):
  POST {WEBAPP_CALLBACK_URL}/api/productions/callback
  body: { productionId, status: 'failed'|'queued', error, retryCount, jobId }
- production_id 없으면 콜백 스킵 (기존 테스트 job 호환)

## n8n 배포 주의사항 (중요)
- n8n 2.6.4 publish 시스템: CLI import는 draft만 업데이트, activeVersionId 미갱신
- 배포 순서: import → DB workflow_history 노드 갱신 → activeVersionId 동기화 → active=true → restart
- import 실행 시 자동 deactivate됨

## Worker YouTube 업로드 구조
- Code 노드 1개로 통합 (upload-youtube)
- 환경변수로 OAuth token refresh (YT_CLIENT_ID/SECRET/REFRESH_TOKEN)
- Node.js native https 모듈로 바이너리 PUT (this.helpers.httpRequest EPIPE 우회)

## Seedance API 제약
- duration: "4" 또는 "8"만 허용
- input_urls: 직접 .jpg/.png URL만 가능 (리다이렉트 URL 불가)
