# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

## Current Status
Worker 파이프라인 테스트: 번역 → 이미지 → TTS 까지 성공, Creatomate 렌더링 템플릿 미생성

## Goal
Creatomate 쇼츠 템플릿 생성 → 풀 파이프라인 완성

## Next Actions
1. [ ] Creatomate 쇼츠 템플릿 생성 (9:16, 이미지+텍스트+오디오)
2. [ ] Worker Creatomate 노드에 template_id 연결
3. [ ] 풀 파이프라인 재테스트 (렌더링 → YouTube 업로드)
4. [ ] Next.js 프론트 프로젝트 초기화

## Last Run
테스트 Job: 0b87f808-d0d4-478f-b02e-db214eaa79d7
결과: 번역(Claude) ✅ → 이미지(kie.ai) ✅ → TTS(kie.ai) ✅ → Creatomate ❌ (template_id 없음)
위치: Production (VPS)

## n8n 워크플로우 ID
- AO Producer: XV5shW265ht59MTD (active)
- AO Worker: FHYohZccExR24Uha (active)

## n8n 크리덴셜 ID
- Postgres: 4W3WKJLsJKa9hVAA
- KieAI (TTS+Image): OipYAEtrzhD1lJmL
- Creatomate API: 7uzM44eLOitv8ubQ
- Claude API: mr2FTmB2pmyvlbWK
- YouTube OAuth2: FHvjDOGBtI0zvyFA

## VPS 환경변수 (docker-compose)
- KIEAI_API_KEY, CREATOMATE_API_KEY, N8N_BLOCK_ENV_ACCESS_IN_NODE=false

## Blockers
- Creatomate 쇼츠 템플릿 미생성
