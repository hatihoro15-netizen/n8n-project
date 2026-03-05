# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

## Current Status
외부 API 크리덴셜 전체 연결 완료 (5건) + YouTube OAuth 브라우저 인증 대기

## Goal
Worker 실제 동작 검증 (이미지 생성 → TTS → 렌더 → 업로드)

## Next Actions
1. [ ] YouTube OAuth 브라우저 인증 (n8n 웹 에디터 > Credentials > Sign in with Google)
2. [ ] Worker 풀 파이프라인 테스트 (실제 영상 생성)
3. [ ] Next.js 프론트 프로젝트 초기화

## Last Run
커맨드: n8n API로 YouTube OAuth2 credential 생성 + Worker 노드 연결
결과: credential 생성 완료, 업로드 노드 연결 완료, OAuth 토큰 미발급 (브라우저 인증 필요)
위치: Production (VPS)
Last Commit: feat: YouTube OAuth 연결 완료

## n8n 워크플로우 ID
- AO Producer: XV5shW265ht59MTD (active)
- AO Worker: FHYohZccExR24Uha (active)

## n8n 크리덴셜 ID
- Postgres: 4W3WKJLsJKa9hVAA
- Replicate API: iG2Q9pXtGuE2xdoS
- KieAI TTS: OipYAEtrzhD1lJmL
- Creatomate API: 7uzM44eLOitv8ubQ
- Claude API: mr2FTmB2pmyvlbWK
- YouTube OAuth2: FHvjDOGBtI0zvyFA

## Blockers
- YouTube OAuth 브라우저 인증 필요 (n8n 웹 에디터에서 Google 로그인)
