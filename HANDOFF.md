# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

## Current Status
외부 API 크리덴셜 3건 연결 완료 (Replicate / kie.ai TTS / Creatomate)

## Goal
Worker 실제 동작 검증 (이미지 생성 → TTS → 렌더 → 업로드)

## Next Actions
1. [ ] Claude API 크리덴셜 생성 + 번역 노드 연결
2. [ ] Worker 풀 파이프라인 테스트 (실제 영상 생성)
3. [ ] YouTube OAuth 크리덴셜 설정
4. [ ] Next.js 프론트 프로젝트 초기화

## Last Run
커맨드: curl -s API 테스트 (Replicate/kie.ai/Creatomate)
결과: 3개 API 모두 인증 성공 (200/400 정상 응답)
위치: Production (VPS)
Last Commit: feat: 외부 API 크리덴셜 연결 완료

## n8n 워크플로우 ID
- AO Producer: XV5shW265ht59MTD (active)
- AO Worker: FHYohZccExR24Uha (active)
- Postgres Credential: 4W3WKJLsJKa9hVAA

## 외부 API 크리덴셜 ID (n8n)
- Replicate API: iG2Q9pXtGuE2xdoS
- KieAI TTS: OipYAEtrzhD1lJmL
- Creatomate API: 7uzM44eLOitv8ubQ

## Blockers
- Claude API 키 미확보 (번역 노드)
- YouTube OAuth 미설정
