# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

## Current Status
- 번역(Claude) ✅ / Seedance(kie.ai) ✅ / TTS(kie.ai) ✅ / Creatomate 합성 ✅ / YouTube 업로드 ✅
- 웹앱 콜백 연동 ✅ / 통합 payload 구조 변경 ✅
- payload: clips[] → files[] (type, url, vision_analysis, video_analysis, use_directly)
- Worker: use_directly=true만 Seedance 씬 생성, 모든 분석 결과는 프롬프트에 반영

## Goal
웹앱 E2E 테스트 (새 payload 구조로)

## Next Actions
1. [ ] 프론트에서 files[] 구조 payload 전송 → E2E 테스트
2. [ ] use_directly=false 파일의 분석 결과 반영 확인
3. [ ] 멀티씬 3개 이상 테스트

## Last Run
배포: 통합 payload 구조 변경 (clips[] → files[] + use_directly)
커밋: feat: AO Worker 통합 payload 구조 변경 대응

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

## Payload 구조 (새)
```json
{
  "prompt_p1": "메인 프롬프트",
  "topic": "주제",
  "keywords": "키워드",
  "category": "카테고리",
  "clip_duration": 5,
  "productionId": "웹앱 production ID",
  "files": [
    { "type": "image", "url": "...", "vision_analysis": "...", "use_directly": true },
    { "type": "video", "url": "...", "video_analysis": "...", "use_directly": false }
  ]
}
```

## 프롬프트 조립 로직
- 모든 파일의 vision_analysis/video_analysis → 프롬프트 앞에 추가 (유/무 관계없이)
- P1 원문 100% 보존 (뒤에 그대로 붙임)
- use_directly=true → Seedance에 이미지 직접 전달
- use_directly=false → 분석 결과만 프롬프트에 반영, Seedance에 미전달

## n8n 배포 주의사항 (중요)
- n8n 2.6.4 publish 시스템: CLI import는 draft만 업데이트, activeVersionId 미갱신
- 배포 순서: import → DB workflow_history 노드 갱신 → activeVersionId 동기화 → active=true → restart
- import 실행 시 자동 deactivate됨

## Seedance API 제약
- duration: "4" 또는 "8"만 허용
- input_urls: 직접 .jpg/.png URL만 가능 (리다이렉트 URL 불가)
