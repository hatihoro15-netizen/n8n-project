# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

## Current Status
- 번역(Claude) ✅ / 이미지(kie.ai) ✅ / TTS(kie.ai) ✅ / Creatomate 렌더링 ✅ / YouTube OAuth ✅
- template_id 056a9082-710f-4345-b964-c6384103fbf6 하드코딩으로 렌더링 성공
- Next.js 웹앱 미생성

## Goal
웹앱 구축 + 나레이션 스크립트 노드 추가

## Next Actions
1. [ ] Next.js 웹앱 초기화 (web/ 디렉토리)
2. [ ] 프롬프트 입력칸 + 사진 첨부칸 UI
3. [ ] 나레이션 스크립트 생성 노드 추가 (Claude API → narration_script → TTS)

## Last Run
커밋: e4fb0b0 feat: Worker 파이프라인 전면 수정 — 렌더링까지 성공
결과: 번역→이미지→TTS→Creatomate 렌더링 전부 성공

## Blockers
없음

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
- KIEAI_API_KEY, CREATOMATE_API_KEY, N8N_BLOCK_ENV_ACCESS_IN_NODE=false
