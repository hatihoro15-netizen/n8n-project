# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> ✅ 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.
> (여기엔 최신 상태/Next/LastRun/Blockers만 유지)

## Current Status
- 번역(Claude) ✅ / TTS(edge-tts) ✅ / Creatomate 합성 ✅ / YouTube 업로드 ⚠️
- 웹앱 콜백 연동 ✅ / 통합 payload 구조 변경 ✅ / 프롬프트 자동 생성 ✅
- Kling AI 3.0 연동 ✅ / 슬라이드쇼 모드 ✅
- production_mode 분기: ai_video (Kling 3.0) / slideshow (edge-tts + NCA FFmpeg)
- prompt_p1 optional: 없으면 topic+keywords+분석결과로 자동 프롬프트 생성
- 슬라이드쇼: edge-tts 나레이션 + NCA FFmpeg 합성 (drawtext 자막 + BGM 루프 + SFX 전환)

## Goal
YouTube 업로드 require('https') 차단 해결 → 전체 E2E 완성

## Next Actions
1. [ ] YouTube 업로드 require('https') 차단 해결 (n8n Task Runner 제한)
2. [ ] 슬라이드쇼 모드 E2E 완료 (렌더링까지 성공, 업로드만 남음)
3. [ ] Kling AI E2E 완료 (렌더링까지 성공, 업로드만 남음)
4. [ ] 4케이스 프롬프트 분기 E2E 테스트

## Last Run
커맨드: VPS 배포 (Producer + Worker import → DB sync → restart)
결과: 슬라이드쇼 E2E — edge-tts + NCA FFmpeg 렌더링 성공 ✅, YouTube 업로드 차단 ⚠️
위치: VPS (76.13.182.180)
테스트 Job: 79495ae0 (status=uploading, rendered_video_url 생성 완료)
Last Commit: feat: 슬라이드쇼 edge-tts + NCA FFmpeg 합성 (onca 방식)

## Blockers
- YouTube 업로드: n8n Task Runner가 require('https') 차단 → native https PUT 불가
  - ai_video / slideshow 양쪽 모두 영향
  - 대안: HTTP Request 노드 사용, 외부 스크립트 호출, Task Runner 설정 변경

## n8n 워크플로우 ID
- AO Producer: XV5shW265ht59MTD (active)
- AO Worker: FHYohZccExR24Uha (active)

## n8n 크리덴셜 ID
- Postgres: 4W3WKJLsJKa9hVAA
- KieAI (TTS+Image+Video): OipYAEtrzhD1lJmL
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
  "production_mode": "ai_video | slideshow",
  "clip_duration": 8,
  "slide_duration": 3,
  "productionId": "웹앱 production ID",
  "files": [
    { "type": "image", "url": "...", "vision_analysis": "...", "use_directly": true }
  ]
}
```

## production_mode 분기
| 모드 | 처리 |
|------|------|
| ai_video (기본) | Kling 3.0 → 영상 1개 → Creatomate 합성 → YouTube |
| slideshow | edge-tts 나레이션 → NCA FFmpeg (이미지+자막+BGM+SFX) → YouTube |

## 슬라이드쇼 NCA FFmpeg 구성
- edge-tts: `POST http://172.17.0.1:5100/tts` (voice_id, emotion, tempo)
  - 반환: audio_url, duration_sec, timestamps[]
- NCA FFmpeg: `POST http://76.13.182.180:8080/v1/ffmpeg/compose` (x-api-key: nca-sagong-2026)
  - inputs: 이미지들, TTS 오디오, BGM 루프, SFX 전환음
  - filter_complex: scale+concat, amix(1:1:0.8), drawtext 자막 (timestamp 기반)
  - BGM: http://76.13.182.180:9000/audio/bgm_new.mp3
  - SFX: http://76.13.182.180:9000/audio/sfx_ppook.wav

## 프롬프트 조립 로직 (4케이스)
| 케이스 | 파일 | P1 | 동작 |
|--------|------|-----|------|
| 1 | O | O | 분석결과 + P1 100% 보존 |
| 2 | O | X | 분석결과 + topic/keywords 자동 프롬프트 |
| 3 | X | O | P1만 반영, text_only 씬 생성 |
| 4 | X | X | 에러 반환 (제작 불가) |

## n8n 배포 주의사항 (중요)
- n8n 2.6.4 publish 시스템: CLI import는 draft만 업데이트, activeVersionId 미갱신
- 배포 순서: import → DB activeVersionId 동기화 → active=true → restart
- import 실행 시 자동 deactivate됨
- docker-compose 경로: /docker/n8n/
- workflow_history 테이블 PK 컬럼명: versionId (id 아님)

## Kling AI 3.0 (kie.ai) 스펙
- 모델: kling-3.0/video
- duration: 3~15초 (정수)
- image_urls: 최대 2장
- aspect_ratio: 9:16 / 16:9 / 1:1
- mode: std / pro
