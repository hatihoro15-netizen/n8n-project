# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

## Current Status
n8n Producer/Worker 크리덴셜 연결 + Activate + 웹훅 테스트 완료

## Goal
Worker 실제 동작 검증 (이미지 생성 → TTS → 렌더 → 업로드)

## Next Actions
1. [ ] 외부 API 키 설정 (Replicate, ElevenLabs, Creatomate, YouTube OAuth)
2. [ ] Worker 풀 파이프라인 테스트 (실제 영상 생성)
3. [ ] Next.js 프론트 프로젝트 초기화

## Last Run
커맨드: curl -X POST .../webhook/ao-produce (테스트 데이터)
결과: job_id=032ae279-5ebf-4ee0-a917-980f3b7dd682, status=processing
위치: Production (VPS)
Last Commit: feat: 크리덴셜 연결 + activate 완료

## n8n 워크플로우 ID
- AO Producer: XV5shW265ht59MTD (active)
- AO Worker: FHYohZccExR24Uha (active)
- Postgres Credential: 4W3WKJLsJKa9hVAA

## Blockers
- 외부 API 키 미확보 (Replicate, ElevenLabs, Creatomate, YouTube OAuth)
