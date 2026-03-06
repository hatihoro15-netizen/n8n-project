# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> ✅ 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.
> (여기엔 최신 상태/Next/LastRun/Blockers만 유지)

## Current Status
- 번역(Claude) ✅ / TTS(kie.ai ElevenLabs) ✅ / NCA FFmpeg 합성 ✅ / YouTube 업로드 ⏸️
- 이미지 생성 웹훅 ✅ (Whisk 방식 subject/scene/style 슬롯)
- Kling AI 3.0 ✅ / 슬라이드쇼 ✅ / 영상화 ✅
- production_mode 분기: ai_video / slideshow
- use_mode 분기: direct / generate / analysis_only
- YouTube 업로드 일시 비활성화 (나중에 별도 작업)

## Goal
프론트 웹앱 연동

## Next Actions
1. [ ] YouTube 업로드 활성화 (별도 작업 예정)
2. [ ] 프론트 웹앱 연동
3. [ ] use_mode generate/analysis_only E2E 테스트

## Last Run
커맨드: VPS 배포 (Image Generator + Worker import → DB sync → restart)
결과: 이미지 생성 웹훅 E2E ✅ (3장 생성 + MinIO 저장 확인)
위치: VPS (76.13.182.180)
테스트: /webhook/ao-generate-image → 3장 생성 → MinIO arubto/generated/ 저장 ✅
Last Commit: feat: 이미지 생성 웹훅 추가 (Whisk 방식)

## Blockers
- YouTube 업로드: require('https'), fetch(), httpRequest PUT(EPIPE) 모두 실패
  - Code v1(vm2) 시도 중이었으나 사용자 요청으로 중단, 나중에 별도 작업

## n8n 워크플로우 ID
- AO Producer: XV5shW265ht59MTD (active)
- AO Worker: FHYohZccExR24Uha (active)
- AO Image Generator: d5b35fb7f1724e448 (active)

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
- MINIO_BUCKET=arubto, MINIO_BASE_URL=http://76.13.182.180:9000

## VPS docker-compose 경로
- /docker/n8n/docker-compose.yml

## 이미지 생성 웹훅 (/webhook/ao-generate-image)
```json
{
  "prompt": "프롬프트 (필수)",
  "aspect_ratio": "9:16 | 16:9 | 1:1",
  "count": 1 | 2 | 3,
  "slots": {
    "subject": { "url": "MinIO URL", "vision_analysis": "분석결과", "use": true },
    "scene": { "url": "MinIO URL", "vision_analysis": "분석결과", "use": true },
    "style": { "url": "MinIO URL", "vision_analysis": "분석결과", "use": true }
  }
}
```
- 응답: `{ success, count, images: [MinIO URLs], prompt, aspect_ratio, slots_used }`
- MinIO 저장 경로: arubto/generated/{timestamp}_{index}.jpg
- MinIO generated/ 경로: 인증 없이 PUT 가능 (anonymous upload 정책)

## 영상 제작 웹훅 (/webhook/ao-produce) Payload
```json
{
  "prompt_p1": "(optional) 메인 프롬프트/나레이션",
  "topic": "주제",
  "keywords": "키워드",
  "category": "카테고리",
  "production_mode": "ai_video | slideshow",
  "clip_duration": 8,
  "files": [
    { "type": "image", "url": "MinIO URL", "vision_analysis": "분석결과",
      "use_mode": "direct | generate | analysis_only", "auto_prompt": "..." }
  ],
  "generated_images": ["이미지 URL 배열"]
}
```

## n8n 배포 주의사항 (중요)
- n8n 2.6.4 publish 시스템: CLI import는 draft만 업데이트, activeVersionId 미갱신
- 배포 순서: import → DB activeVersionId 동기화 → active=true → restart
- import 실행 시 자동 deactivate됨
- workflow_history 테이블 PK 컬럼명: versionId (id 아님)

## n8n Task Runner 제한사항
- require('https'), require('http') 등 Node.js 내장 모듈 사용 불가
- URL 클래스, fetch() 사용 불가
- this.helpers.httpRequest PUT 바이너리 → EPIPE 에러
- NCA FFmpeg -shortest: argument 비워두면 오류 → -t 사용
- NCA FFmpeg URL: 파일 확장자 필수 (ensureExtension 자동 보정)

## Kling AI 3.0 (kie.ai) 스펙
- 모델: kling-3.0/video, duration: 3~15초, image_urls: 최대 2장
- aspect_ratio: 9:16 / 16:9 / 1:1, mode: std / pro
