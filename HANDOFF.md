# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> ✅ 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.
> (여기엔 최신 상태/Next/LastRun/Blockers만 유지)

## Current Status
- 번역(Claude) ✅ / TTS(kie.ai ElevenLabs) ✅ / NCA FFmpeg 합성 ✅ / YouTube 업로드 ⏸️ (일시 비활성화)
- 웹앱 콜백 연동 ✅ / 통합 payload 구조 ✅ / 프롬프트 자동 생성 ✅
- Kling AI 3.0 ✅ / 슬라이드쇼 ✅ / 영상화 ✅
- production_mode 분기: ai_video (Kling 3.0 + NCA FFmpeg) / slideshow (이미지 + NCA FFmpeg)
- use_mode 분기: direct / generate / analysis_only
- 양쪽 모드 모두 NCA FFmpeg 합성 (TTS + 자막 + BGM + SFX)
- YouTube 업로드 일시 비활성화 (나중에 활성화)

## Goal
YouTube 업로드 활성화 → 프론트 웹앱 연동

## Next Actions
1. [ ] YouTube 업로드 활성화 (require('https') 해결 또는 대안)
2. [ ] use_mode generate/analysis_only E2E 테스트 (kie.ai 이미지 생성)
3. [ ] generated_images 필드 E2E 테스트
4. [ ] 프론트 웹앱 연동

## Last Run
커맨드: VPS 배포 (Producer + Worker import → DB sync → restart)
결과: 슬라이드쇼 E2E ✅ + 영상화 E2E ✅ (NCA FFmpeg 합성 성공, YouTube 스킵)
위치: VPS (76.13.182.180)
테스트 Job (슬라이드쇼): 599c3af3 → uploaded ✅
테스트 Job (영상화): c1ea1a83 → uploaded ✅
Last Commit: fix: NCA FFmpeg URL 확장자 + -shortest 옵션 수정 + YouTube 업로드 스킵

## Blockers
- YouTube 업로드: n8n Task Runner가 require('https') 차단 → 일시 비활성화 상태
  - 나중에 활성화 예정

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
- MINIO_BUCKET=arubto, MINIO_BASE_URL=http://76.13.182.180:9000

## VPS docker-compose 경로
- /docker/n8n/docker-compose.yml

## Payload 구조
```json
{
  "prompt_p1": "(optional) 메인 프롬프트/나레이션",
  "topic": "주제",
  "keywords": "키워드",
  "category": "카테고리",
  "production_mode": "ai_video | slideshow",
  "clip_duration": 8,
  "slide_duration": 3,
  "productionId": "웹앱 production ID",
  "files": [
    {
      "type": "image",
      "url": "MinIO URL",
      "vision_analysis": "Claude Vision 분석결과",
      "use_mode": "direct | generate | analysis_only",
      "auto_prompt": "analysis_only 시 자동 프롬프트"
    }
  ],
  "generated_images": ["Step1에서 생성된 이미지 URL 배열"]
}
```

## production_mode 분기
| 모드 | 처리 |
|------|------|
| ai_video (기본) | use_mode별 이미지 처리 → Kling 3.0 → NCA FFmpeg (영상+TTS+자막+BGM+SFX) |
| slideshow | use_mode별 이미지 처리 → NCA FFmpeg (이미지슬라이드+TTS+자막+BGM+SFX) |

## use_mode 분기
| 모드 | 동작 |
|------|------|
| direct | 원본 이미지 그대로 사용 |
| generate | vision_analysis 기반 비슷한 새 이미지 생성 (kie.ai) |
| analysis_only | auto_prompt 기반 완전 새 이미지 생성 (kie.ai) |

## NCA FFmpeg 합성 구성
- TTS: kie.ai (ElevenLabs multilingual v2, voice_id: EXAVITQu4vr4xnSDxMaL)
- NCA FFmpeg: POST http://76.13.182.180:8080/v1/ffmpeg/compose (x-api-key: nca-sagong-2026)
  - filter_complex: scale+concat, amix(TTS:BGM:SFX = 1:1:0.8), drawtext 자막
  - 자막 타이밍: 문장 분리 + 글자수 비율 배분
  - BGM: http://76.13.182.180:9000/audio/bgm_new.mp3 (루프 + 끝 2초 페이드아웃)
  - SFX: http://76.13.182.180:9000/audio/sfx_ppook.wav (이미지/장면 전환)
- NCA FFmpeg URL 제한: 파일 확장자 필수 (ensureExtension 함수로 자동 보정)

## n8n 배포 주의사항 (중요)
- n8n 2.6.4 publish 시스템: CLI import는 draft만 업데이트, activeVersionId 미갱신
- 배포 순서: import → DB activeVersionId 동기화 → active=true → restart
- import 실행 시 자동 deactivate됨
- docker-compose 경로: /docker/n8n/
- workflow_history 테이블 PK 컬럼명: versionId (id 아님)

## n8n Task Runner 제한사항
- require('https'), require('http') 등 Node.js 내장 모듈 사용 불가
- URL 클래스 사용 불가
- NCA FFmpeg -shortest 옵션: argument 비워두면 파일명으로 해석됨 → -t 사용

## Kling AI 3.0 (kie.ai) 스펙
- 모델: kling-3.0/video
- duration: 3~15초 (정수)
- image_urls: 최대 2장
- aspect_ratio: 9:16 / 16:9 / 1:1
- mode: std / pro
