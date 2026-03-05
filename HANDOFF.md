# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> ✅ 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.
> (여기엔 최신 상태/Next/LastRun/Blockers만 유지)

## Current Status
- 번역(Claude) ✅ / Seedance(kie.ai) ✅ / TTS(kie.ai) ✅ / Creatomate 합성 ✅ / YouTube 업로드 ✅
- 웹앱 콜백 연동 ✅ / 통합 payload 구조 변경 ✅ / 프롬프트 자동 생성 ✅
- payload: clips[] → files[] (type, url, vision_analysis, video_analysis, use_directly)
- Worker: use_directly=true만 Seedance 씬 생성, 모든 분석 결과는 프롬프트에 반영
- prompt_p1 optional: 없으면 topic+keywords+분석결과로 자동 프롬프트 생성

## Goal
웹앱 E2E 테스트 (4케이스 프롬프트 분기)

## Next Actions
1. [ ] 케이스1 테스트: 파일 O + 프롬프트 O
2. [ ] 케이스2 테스트: 파일 O + 프롬프트 X (자동 프롬프트)
3. [ ] 케이스3 테스트: 파일 X + 프롬프트 O (텍스트 전용)

## Last Run
커맨드: VPS 배포 (Producer + Worker import → DB sync → restart)
결과: Producer + Worker active ✅
위치: VPS (76.13.182.180)
Last Commit: feat: AO Worker 프롬프트 자동 생성 로직 추가

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
- KIEAI_API_KEY, CREATOMATE_API_KEY, YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
- WEBAPP_CALLBACK_URL=https://api-n8n.xn--9g4bn4fm2bl2mb9f.com
- N8N_BLOCK_ENV_ACCESS_IN_NODE=false

## VPS docker-compose 경로
- /docker/n8n/docker-compose.yml

## Payload 구조
```json
{
  "prompt_p1": "(optional) 메인 프롬프트",
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

## 프롬프트 조립 로직 (4케이스)
| 케이스 | 파일 | P1 | 동작 |
|--------|------|-----|------|
| 1 | O | O | 분석결과 + P1 100% 보존 |
| 2 | O | X | 분석결과 + topic/keywords 자동 프롬프트 |
| 3 | X | O | P1만 반영, text_only 씬 생성 |
| 4 | X | X | 에러 반환 (제작 불가) |

## n8n 배포 주의사항 (중요)
- n8n 2.6.4 publish 시스템: CLI import는 draft만 업데이트, activeVersionId 미갱신
- 배포 순서: import → DB workflow_history 노드 갱신 → activeVersionId 동기화 → active=true → restart
- import 실행 시 자동 deactivate됨
- docker-compose 경로: /docker/n8n/

## Seedance API 제약
- duration: "4" 또는 "8"만 허용
- input_urls: 직접 .jpg/.png URL만 가능 (리다이렉트 URL 불가)
