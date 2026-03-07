# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> ✅ 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.
> (여기엔 최신 상태/Next/LastRun/Blockers만 유지)

## Current Status
- 번역(Claude Code 노드) ✅ / TTS(kie.ai ElevenLabs) ✅ / NCA FFmpeg 합성 ✅ / YouTube 업로드 ⏸️
- 이미지 생성 웹훅 ✅ (Whisk 방식, kie.ai URL 직접 반환)
- Kling AI 3.0 ✅ / 슬라이드쇼 ✅ / 영상화 ✅
- production_mode 분기: ai_video / slideshow
- use_mode 분기: direct / generate / analysis_only
- aspect_ratio 분기: 9:16 (세로/숏폼) / 16:9 (가로/롱폼)
- 나레이션 자동생성 ✅ (Claude API, narration_script 우선)
- 중간 콜백 4개 ✅ (processing / rendering / generated / uploaded)
- 콜백 videoUrl 필드 ✅ (generated + uploaded 콜백에 videoUrl/renderedVideoUrl 포함)
- YouTube 업로드 일시 비활성화 (나중에 별도 작업)
- Worker 영상 품질 개선 ✅
- BGM/SFX 기본 OFF ✅
- Producer SQL 이스케이프 ✅
- **P0 뼈대 구현 ✅**: Prompt Lock + Last-Edit Priority + Length Gate
  - prompt_hash: DB 저장 + Worker 비교 ✅
  - Last-Edit Priority: prompt_p1 단일 소스, topic/keywords/category 재조합 금지 ✅
  - Length Gate: duration 허용값 검증 + clip_count 재계산 + strict_mode 분기 ✅
  - verify_mode: output_hash를 ao_job_logs에 기록 ✅
  - topic/keywords/category: 필수→선택 변경 ✅
- **P0-2 수정 ✅**: Prompt Lock 재생성 연결 + 30초 길이 이슈 수정
  - Prompt Lock IF 분기: assemble-prompt 후 IF 노드로 분기 처리 ✅
  - Prompt Lock 재생성: 불일치 시 최신 prompt_p1로 재조립 후 진행 ✅
  - 렌더 전 2차 확인: DB에서 prompt_hash 재조회 + 불일치 시 에러 ✅
  - 나레이션 길이 보정: target_duration 기반 글자수 지시 (4.5자/초) ✅
  - Length Gate 통과 기준: strict=target±1초, soft=target-3초~target+1초 ✅
  - clip_count 보정: 짧으면 클립 반복, 길면 분할 ✅
  - 30초 케이스: 19.1초 → 31.3초 (목표 근처 도달) ✅
- **engine_type 분기 골격 ✅**:
  - Producer: engine_type 수신/검증 (기본 core_message, 5종 허용)
  - Producer: Switch 노드 골격 추가 (현재 모든 경로 공통 합류, Phase 4에서 분기)
  - DB: engine_type 컬럼 추가
  - Worker: engine_type 값 전달받아 실행 (변경 없음)

## Goal
프론트 웹앱 연동

## Next Actions
1. [ ] 프론트 웹앱 연동
2. [ ] NCA 한글 자막 폰트 영구화 (컨테이너 재시작 시 사라짐)
3. [ ] 이미지 생성 웹훅 MinIO 바이너리 저장 (별도 작업 예정)
4. [ ] YouTube 업로드 활성화 (별도 작업 예정)

## Last Run
커맨드: P0-2 — Prompt Lock 재생성 연결 + 30초 길이 이슈 수정
결과:
- Prompt Lock: IF 분기 + 재생성 노드 + 렌더 전 2차 확인 추가
- 나레이션: target_duration 기반 글자수 지시 + TTS 짧으면 재생성 1회
- Length Gate: strict=target±1초, soft=target-3초 이상 통과 기준
- clip_count: 짧으면 클립 반복, 길면 분할 보정
- 30초 테스트: 19.1초 → 31.3초 (over_soft, 목표 근처 도달)
위치: Local + VPS (76.13.182.180)
Last Commit: (pending)

## Blockers
- YouTube 업로드: Code v1(vm2) 시도 중이었으나 사용자 요청으로 중단
- NCA toolkit: GUNICORN_TIMEOUT 미설정 시 기본 30초로 worker kill됨
- NCA 한글 자막: fonts-nanum 컨테이너 재시작 시 사라짐
- kie.ai TTS: 간헐적 internal error 발생 (일시적, 재시도로 해결)

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
- CLAUDE_API_KEY (번역 + 나레이션 생성용)
- WEBAPP_CALLBACK_URL=https://api-n8n.xn--9g4bn4fm2bl2mb9f.com
- N8N_BLOCK_ENV_ACCESS_IN_NODE=false
- MINIO_BUCKET=arubto, MINIO_BASE_URL=http://76.13.182.180:9000

## VPS docker-compose 경로
- /docker/n8n/docker-compose.yml

## n8n 컨테이너 이름 (중요)
- n8n 메인: n8n-n8n-1
- n8n worker: n8n-n8n-worker-1
- postgres: n8n-postgres

## NCA toolkit 실행 (중요)
- `docker run -d --name nca-toolkit --restart always -p 8080:8080 -e API_KEY=nca-sagong-2026 -e S3_ENDPOINT_URL=http://76.13.182.180:9000 -e S3_ACCESS_KEY=admin -e S3_SECRET_KEY=NcaMin10S3cure! -e S3_BUCKET_NAME=nca-toolkit -e S3_REGION=us-east-1 -e GUNICORN_TIMEOUT=600 stephengpope/no-code-architects-toolkit:latest`

## 이미지 생성 웹훅 (/webhook/ao-generate-image)
```json
{
  "prompt": "프롬프트 (필수)",
  "aspect_ratio": "9:16 | 16:9",
  "count": 1 | 2 | 3,
  "slots": {
    "subject": { "url": "MinIO URL", "vision_analysis": "분석결과", "use": true },
    "scene": { "url": "MinIO URL", "vision_analysis": "분석결과", "use": true },
    "style": { "url": "MinIO URL", "vision_analysis": "분석결과", "use": true }
  }
}
```

## 영상 제작 웹훅 (/webhook/ao-produce) Payload
```json
{
  "prompt_p1": "(필수) 메인 프롬프트/나레이션",
  "topic": "(선택) 주제 — 저장/표시 전용",
  "keywords": "(선택) 키워드 — 저장/표시 전용",
  "category": "(선택) 카테고리 — 저장/표시 전용",
  "duration": 30,
  "strict_mode": false,
  "verify_mode": false,
  "production_mode": "ai_video | slideshow",
  "aspect_ratio": "9:16 | 16:9",
  "clip_duration": 8,
  "narration_script": "(optional) 직접 입력 나레이션",
  "enable_bgm": false,
  "enable_sfx": false,
  "bgm_url": "(optional) 커스텀 BGM URL",
  "files": [
    { "type": "image", "url": "MinIO URL", "vision_analysis": "분석결과",
      "use_mode": "direct | generate | analysis_only", "auto_prompt": "..." }
  ],
  "generated_images": ["이미지 URL 배열"]
}
```

## 콜백 필드 (웹앱으로 전송)
- processing: `{ productionId, status, jobId }`
- rendering: `{ productionId, status, jobId }`
- generated: `{ productionId, status, jobId, videoUrl, renderedVideoUrl, output_hash, length_gate_status }`
- uploaded: `{ productionId, status, jobId, youtubeVideoId, youtubeUrl, renderedVideoUrl, videoUrl }`

## P0 입력 계약
- prompt_p1: 필수 (단일 소스, 절대 변경 금지)
- topic/keywords/category: 선택 (저장/표시 전용, 생성 영향 금지)
- duration: 선택 (30/40/50/60/90/120/150/180만 허용)
- strict_mode: 선택 (기본 false, true=Length Gate 하드 차단)
- verify_mode: 선택 (기본 false, true=output_hash 기록)
- prompt_hash: 자동 생성 (FNV-1a)

## Length Gate 스펙
- 통과 기준: strict=target±1초, soft=target-3초~target+1초
- 보정: clip_count 재계산 (짧으면 클립 반복, 길면 분할)
- 나레이션: target_duration 기반 글자수 지시 + 짧으면 재생성 1회
- strict_mode=true 범위 밖: LENGTH_GATE_BLOCKED 에러
- length_gate_status: no_gate / pass / corrected_short / corrected_long / under_soft / over_soft / blocked_short / blocked_long

## Verify Mode 스펙
- output_hash 기록 위치: ao_job_logs(detail.output_hash)
- 10회 반복: 외부 호출자가 동일 payload로 10회 호출
- 비교 기준: job_logs에서 동일 prompt_hash의 output_hash 일치 여부

## aspect_ratio별 해상도
- 9:16 → 1080x1920 (세로/숏폼)
- 16:9 → 1920x1080 (가로/롱폼)

## n8n 배포 주의사항 (중요)
- n8n 2.6.4 publish 시스템: CLI import는 draft만 업데이트, activeVersionId 미갱신
- 배포 순서: import → DB activeVersionId 동기화 → active=true → restart
- import 실행 시 자동 deactivate됨
- workflow_history 테이블 PK 컬럼명: versionId (id 아님)
- 환경변수 변경 시: docker compose up -d (restart는 env 미적용)

## n8n Task Runner 제한사항
- require('https'), require('http') 등 Node.js 내장 모듈 사용 불가
- URL 클래스, fetch() 사용 불가
- this.helpers.httpRequest PUT 바이너리 → EPIPE 에러
- httpRequest 노드 jsonBody 템플릿: 특수문자 이스케이프 안됨 → Code 노드 사용
- NCA FFmpeg -shortest: argument 비워두면 오류 → -t 사용
- NCA FFmpeg URL: 파일 확장자 필수 (ensureExtension 자동 보정)
- crypto 모듈 사용 불가 → FNV-1a 해시 사용

## Kling AI 3.0 (kie.ai) 스펙
- 모델: kling-3.0/video, duration: 3~15초, image_urls: 최대 2장
- aspect_ratio: 9:16 / 16:9, mode: std / pro

## Worker 영상 품질 개선 상세 (7항목)
1. 이미지 비율: 정사각 크롭 + 블랙 패딩 (온카 방식)
2. 상단 제목바: topic 표시 (drawbox + drawtext, wrapTitle 2줄 분리)
3. 자막 줄바꿈: 공백 없는 한글 강제 줄바꿈 (max 12자)
4. 자막 타이밍: TTS 실측 길이 기반 (ffprobe)
5. 영상 끝: TTS 실측 duration 사용 (ffprobe fallback)
6. BGM URL: bgm_url 필드로 동적 BGM 지원
7. BGM/SFX 기본 OFF: enable_bgm/enable_sfx 플래그
