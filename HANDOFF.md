# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.
> (여기엔 최신 상태/Next/LastRun/Blockers만 유지)

## Current Status
- 번역(Claude Code 노드) / TTS(kie.ai ElevenLabs) / NCA FFmpeg 합성 / YouTube 업로드 일시정지
- 이미지 생성 웹훅 (Whisk 방식, kie.ai URL 직접 반환)
- Kling AI 3.0 / 슬라이드쇼 / 영상화
- production_mode 분기: ai_video / slideshow
- use_mode 분기: direct / analysis_only (generate 제거)
- aspect_ratio 분기: 9:16 (세로/숏폼) / 16:9 (가로/롱폼)
- 나레이션 자동생성 (Claude API, narration_script 우선)
- 중간 콜백 4개 (processing / rendering / generated / uploaded)
- 콜백 videoUrl 필드 (generated + uploaded 콜백에 videoUrl/renderedVideoUrl 포함)
- YouTube 업로드 일시 비활성화 (나중에 별도 작업)
- Worker 영상 품질 개선
- BGM/SFX 기본 OFF
- **bgm_mode/sfx_mode/sfx_file_url DB 컬럼 + Producer 파싱**:
  - DB: bgm_mode(none/ai_auto/uploaded), sfx_mode(none/ai_auto/uploaded/combined), sfx_file_url
  - Producer: bgm_mode/sfx_mode 검증 + enable_bgm/enable_sfx 하위호환 fallback
  - INSERT SQL에 3개 컬럼 반영
- Producer SQL 이스케이프
- **P0 뼈대 구현**: Prompt Lock + Last-Edit Priority + Length Gate
  - prompt_hash: DB 저장 + Worker 비교
  - Last-Edit Priority: prompt_p1 단일 소스, topic/keywords/category 재조합 금지
  - Length Gate: duration 허용값 검증 + clip_count 재계산 + strict_mode 분기
  - verify_mode: output_hash를 ao_job_logs에 기록
  - topic/keywords/category: 필수->선택 변경
- **P0-2 수정**: Prompt Lock 재생성 연결 + 30초 길이 이슈 수정
- **engine_type 분기 골격**: Producer Switch 노드 골격 (Phase 4에서 분기)
- **narration_style/narration_tone**: Producer 검증 + Worker generateNarration 반영 (SPEC 4조)
- **clip_duration auto 모드**: TTS 실측 기반 Kling duration 자동 결정
- **B-1 direct 모드 이미지**: Kling 전달 수정 (silent fallback 금지)
- **F-7 자막 타이밍 배치 (Claude API)**: buildSubtitleTimings 교체
- **narration_start_sec 처리**:
  - Producer: narration_start_sec 파싱 + metadata JSONB 저장
  - Worker: metadata에서 추출 → adelay로 TTS 시작 오프셋 + 자막 타이밍 동기화
  - 우선순위: 명시값 > scenes[0].duration_sec 기반 자동 > 0초 fallback
- **F-8 영상/나레이션 길이 일체화**: auto 모드 max(tts, scene_duration)
- **F-9 효과음 AI 타이밍 + 동적 배치**:
  - generateSfxTimings: Claude API로 나레이션 타이밍 분석 -> 최대 5개 SFX 배치 시점 결정
  - render-video: 동적 SFX adelay 적용 (hardcoded 500ms -> AI 결정 타이밍)
  - **범위 제한 사유**: 효과음 파일 AI 생성 보류 (API 미확보). 기존 sfx_ppook.wav를 AI 타이밍에 배치.
- **bgm_mode / sfx_mode 대응**:
  - bgm_mode: ai_auto / uploaded / none (enable_bgm 하위 호환 fallback)
  - sfx_mode: ai_auto / uploaded / combined / none (enable_sfx 하위 호환 fallback)
  - sfx_file_url: uploaded/combined 모드에서 사용자 SFX 파일 URL 사용
  - render-video: SFX_ACTIVE_URL로 모드별 SFX 소스 분기
- **F-10 AI 장면-이미지 자동 매칭**:
  - matchImageToScene: Claude API로 vision_analysis + 프롬프트/나레이션 분석 -> 이미지 순서 재배치
  - image_order=auto && 이미지 2장 이상일 때만 동작
  - image_order=sequential(기본): 기존 순서 유지
- **멀티클립 ai_video 렌더링**:
  - Producer: clip_duration_mode auto/fixed 자동 결정 (duration>15 && clip_duration 미지정 -> auto)
  - Worker: clipCount = ceil(targetLen/15), perClipSec = ceil(targetLen/clipCount), 3-15초 clamp
  - Kling 다중 호출: clipCount개 클립 순차 생성 -> FFmpeg concat으로 최종 합성
  - 단일 클립(<=15초): 기존 동작 유지
- **씬별 프롬프트 분배 (scenes[])**:
  - Producer: scenes[] 검증 (duration_sec 3~15, prompt 필수, 합계 vs duration +-3초)
  - Worker: scenes 있으면 clipCount=scenes.length, 클립별 scenes[i].prompt/duration_sec 사용
  - scenes 없으면 기존 동작 유지 (하위 호환)
- **AI 자동 씬 분할**:
  - scenes 없고 clipCount>1일 때 Claude API로 prompt_p1을 클립별 프롬프트로 자동 분할
  - generateScenePrompts: 각 클립에 다른 시각적 장면 생성
  - API 실패 시 promptBase fallback (기존 동작)
- **fail-fast 402 + processing 고착 방지**:
  - process-clips: kie.ai 402 크레딧 부족 시 KIE_CREDIT_INSUFFICIENT 에러 throw
  - process-clips: 전체 try-catch 래퍼 → 에러 시 error JSON 반환
  - render-lock-check: error JSON 감지 시 즉시 throw → 파이프라인 중단
  - render-video/upload-youtube: error passthrough 추가
  - settings.errorWorkflow: 깨진 템플릿 문자열 제거 (빈 문자열로)
- **Watchdog 콜백 전송**:
  - watchdog-check (Postgres): 5분 이상 processing → failed UPDATE + RETURNING
  - watchdog-callback (Code): 각 stuck job에 웹앱 콜백 POST (3회 재시도, exponential backoff)
  - watchdog-log (Postgres): 콜백 실패 시 job_logs에 로그 저장
  - 흐름: 스케줄 트리거 → watchdog-check → watchdog-callback → watchdog-log → pop-queue
  - pop-queue에서 Watchdog SQL 제거 (전용 노드로 분리)

## Goal
프론트 웹앱 연동

## Next Actions
1. [ ] 프론트 웹앱 연동
2. [ ] NCA 한글 자막 폰트 영구화 (컨테이너 재시작 시 사라짐)
3. [ ] 이미지 생성 웹훅 MinIO 바이너리 저장 (별도 작업 예정)
4. [ ] YouTube 업로드 활성화 (별도 작업 예정)
5. [ ] SFX 파일 AI 생성 (SFX 생성 API 확보 시)

## Last Run
커맨드: fix(worker): send callback on watchdog failure and sync webapp status
결과:
- Watchdog을 pop-queue SQL에서 분리 → 전용 3노드 파이프라인
- watchdog-check: processing > 5분 → failed UPDATE + RETURNING
- watchdog-callback: 웹앱 콜백 POST (3회 재시도, exponential backoff 1s/2s/4s)
- watchdog-log: 콜백 실패 시 job_logs INSERT
- stuck production 3건 수동 콜백 전송 (200 OK)
- VPS 배포 완료 + DB 검증 통과
위치: Local + VPS (76.13.182.180)

## Blockers
- kie.ai 크레딧: 충전 완료 (2026-03-08)
- YouTube 업로드: Code v1(vm2) 시도 중이었으나 사용자 요청으로 중단
- NCA toolkit: GUNICORN_TIMEOUT 미설정 시 기본 30초로 worker kill됨
- NCA 한글 자막: fonts-nanum 컨테이너 재시작 시 사라짐
- kie.ai TTS: 간헐적 internal error 발생 (일시적, 재시도로 해결)
- SFX AI 생성: kie.ai/fal.ai에 SFX 생성 모델 없음 (타이밍만 AI 결정)

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
  "engine_type": "core_message",
  "narration_style": "설명형",
  "narration_tone": "차분하게",
  "production_mode": "ai_video | slideshow",
  "aspect_ratio": "9:16 | 16:9",
  "clip_duration": "8 | 0 | 'auto'",
  "narration_script": "(optional) 직접 입력 나레이션",
  "bgm_mode": "none | ai_auto | uploaded",
  "sfx_mode": "none | ai_auto | uploaded | combined",
  "bgm_url": "(optional) 커스텀 BGM URL (uploaded 모드용)",
  "sfx_file_url": "(optional) 사용자 SFX 파일 URL (uploaded/combined 모드용)",
  "image_order": "sequential | auto",
  "scenes": [
    { "prompt": "씬별 프롬프트", "duration_sec": 5 }
  ],
  "files": [
    { "type": "image", "url": "MinIO URL", "vision_analysis": "분석결과",
      "use_mode": "direct | analysis_only", "auto_prompt": "..." }
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
- duration: 선택 (0=자동 또는 3~180 정수)
- strict_mode: 선택 (기본 false, true=Length Gate 하드 차단)
- verify_mode: 선택 (기본 false, true=output_hash 기록)
- engine_type: 선택 (기본 core_message, 5종 허용)
- narration_style: 선택 (기본 설명형, 4종 허용)
- narration_tone: 선택 (기본 차분하게, 4종 허용)
- clip_duration: 선택 (기본 8, 0/'auto'=TTS 실측 기반 자동)
- prompt_hash: 자동 생성 (FNV-1a)

## Length Gate 스펙
- 통과 기준: strict=target+-1초, soft=target-3초~target+1초
- 보정: clip_count 재계산 (짧으면 클립 반복, 길면 분할)
- 나레이션: target_duration 기반 글자수 지시 + 짧으면 재생성 1회
- strict_mode=true 범위 밖: LENGTH_GATE_BLOCKED 에러
- length_gate_status: no_gate / pass / corrected_short / corrected_long / under_soft / over_soft / blocked_short / blocked_long

## Verify Mode 스펙
- output_hash 기록 위치: ao_job_logs(detail.output_hash)
- 10회 반복: 외부 호출자가 동일 payload로 10회 호출
- 비교 기준: job_logs에서 동일 prompt_hash의 output_hash 일치 여부

## clip_duration auto 모드 스펙
- 입력: clip_duration=0 / '0' / 'auto' -> 내부적으로 'auto'로 정규화
- 동작: TTS 실측 길이(ffprobe)를 Kling 영상 duration으로 사용 (3-15초 clamp)
- 실행 순서: 나레이션 생성 -> TTS + ffprobe -> clipDur 결정 -> Kling 영상 생성
- totalDuration: auto시 TTS duration, fixed시 max(clipDur, TTS)
- 출력 추가: clip_duration_mode (auto/fixed), actual_clip_duration
- 기존 고정 모드(clip_duration=8 등): 동작 변화 없음

## aspect_ratio별 해상도
- 9:16 -> 1080x1920 (세로/숏폼)
- 16:9 -> 1920x1080 (가로/롱폼)

## n8n 배포 주의사항 (중요)
- n8n 2.6.4 publish 시스템: CLI import는 draft만 업데이트, activeVersionId 미갱신
- 배포 순서: import -> DB activeVersionId 동기화 -> active=true -> restart
- import 실행 시 자동 deactivate됨
- workflow_history 테이블 PK 컬럼명: versionId (id 아님)
- 환경변수 변경 시: docker compose up -d (restart는 env 미적용)
- n8n API PUT: 추가 속성 거부 -> name/nodes/connections/settings만 전송

## n8n Task Runner 제한사항
- require('https'), require('http') 등 Node.js 내장 모듈 사용 불가
- URL 클래스, fetch() 사용 불가
- this.helpers.httpRequest PUT 바이너리 -> EPIPE 에러
- httpRequest 노드 jsonBody 템플릿: 특수문자 이스케이프 안됨 -> Code 노드 사용
- NCA FFmpeg -shortest: argument 비워두면 오류 -> -t 사용
- NCA FFmpeg URL: 파일 확장자 필수 (ensureExtension 자동 보정)
- crypto 모듈 사용 불가 -> FNV-1a 해시 사용

## Kling AI 3.0 (kie.ai) 스펙
- 모델: kling-3.0/video, duration: 3~15초, image_urls: 최대 2장
- aspect_ratio: 9:16 / 16:9, mode: std / pro

## Worker 영상 품질 개선 상세 (7항목)
1. 이미지 비율: 정사각 크롭 + 블랙 패딩 (온카 방식)
2. 상단 제목바: 제거됨 (drawbox + drawtext 삭제)
3. 자막 줄바꿈: 공백 없는 한글 강제 줄바꿈 (max 12자)
4. 자막 타이밍: TTS 실측 길이 기반 (ffprobe)
5. 영상 끝: TTS 실측 duration 사용 (ffprobe fallback)
6. BGM URL: bgm_url 필드로 동적 BGM 지원
7. BGM/SFX 기본 OFF: enable_bgm/enable_sfx 플래그

## fail-fast / processing 고착 방지 스펙
- process-clips: kie.ai 402 → KIE_CREDIT_INSUFFICIENT throw (try-catch 래퍼)
- render-lock-check: error JSON 감지 → throw → 파이프라인 중단
- render-video/upload-youtube: error passthrough
- Watchdog 3노드: watchdog-check → watchdog-callback → watchdog-log → pop-queue
- Watchdog 콜백: 3회 재시도 (exponential backoff 1s/2s/4s), 실패 시 job_logs 저장
- errorWorkflow: 빈 문자열 (깨진 템플릿 제거됨)
