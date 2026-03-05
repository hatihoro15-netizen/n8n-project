# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

## Current Status
- 번역(Claude) ✅ / Seedance(kie.ai) ✅ / TTS(kie.ai) ✅ / Creatomate 합성 ✅
- 멀티씬 순차 처리 + include_audio 분기 구현 완료
- YouTube OAuth 토큰 만료 → 재인증 필요
- Next.js 웹앱 미생성

## Goal
웹앱 구축 + YouTube OAuth 재인증

## Next Actions
1. [ ] YouTube OAuth 재인증 (n8n 웹 에디터 > Credentials > Sign in with Google)
2. [ ] Next.js 웹앱 초기화 (web/ 디렉토리)
3. [ ] 프롬프트 입력 + 사진 첨부 + include_audio 옵션 UI

## Last Run
커밋: 104f30a feat: 멀티씬 순차처리 + include_audio 분기 + ao-produce 웹훅 활성화
결과: 번역→Seedance→TTS→Creatomate 합성 성공, YouTube 업로드만 OAuth 만료

## Blockers
- YouTube OAuth 토큰 만료 (브라우저에서 수동 재인증 필요)

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

## n8n 배포 주의사항 (중요)
- n8n 2.6.4 publish 시스템: CLI import는 draft만 업데이트, activeVersionId 미갱신
- 배포 순서: import → DB workflow_history 노드 갱신 → activeVersionId 동기화 → active=true → restart
- import 실행 시 자동 deactivate됨 → 반드시 DB에서 active=true 재설정 후 restart

## Seedance API 제약
- duration: "4" 또는 "8"만 허용 ("5", "6" 등 불가)
- input_urls: 직접 .jpg/.png URL만 가능 (리다이렉트 URL 불가)
- 이미지 URL 실패 시 자동으로 텍스트 전용 모드로 재시도
