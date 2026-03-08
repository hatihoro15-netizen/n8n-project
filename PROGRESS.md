# PROGRESS.md — 진행 일지

> ❌ 날짜별 보고서는 append만(삭제/overwrite 금지).
> ✅ 상단 "현재 요약" 섹션만 매 세션 overwrite 가능.
> ✅ Next Actions 정답은 HANDOFF.md에. 여기엔 방향/메모만.

---

## 현재 요약 (이 섹션만 overwrite 가능)
- 마지막 업데이트: 2026-03-08
- 현재 상태(1줄): Watchdog 콜백 전송 + stuck production 정리 완료
- 진행중 작업: 프론트 웹앱 연동
- 최근 완료: Watchdog 3노드 분리 + 실패 콜백 전송 + stuck 3건 수동 정리
- 주의사항: YouTube 비활성화, NCA GUNICORN_TIMEOUT=600 필수

---

## 작업 보고서 (append-only, 양식: docs/07-report-template.md 참조)

## 2026-03-05
### ✅ Done
- [x] ao-pipeline/ 폴더 구조 생성 (docs/, scripts/)
- [x] CLAUDE.md / HANDOFF.md / PROGRESS.md 생성
- [x] docs/01-architecture.md — 시스템 구조 (Producer/Worker/Queue)
- [x] docs/02-db-schema.md — DB 테이블 설계 (ao_jobs, ao_job_media, ao_job_logs, ao_proxy_pool)
- [x] docs/03-seedance-api.md — 씨덴스 API 조사 (엔드포인트/인증/가격/프로바이더)
- [x] docs/04-producer-design.md — n8n Producer 워크플로우 초안 (6노드 구성)
- [x] docs/05-input-schema.md — 입력 스키마 정의 + 검증 규칙
### 🔁 Tried
- 씨덴스 공식 API 조사 → 2026-02 기준 미출시, 서드파티(fal.ai/ModelsLab) 사용 가능 확인
### 📌 Result
- 프로젝트 구조 + 관리 파일 + 설계 문서 완성
- 씨덴스 API: fal.ai(1차) / ModelsLab(2차) 권장, Bearer 토큰 인증, 비동기 폴링 방식
- Producer 설계: Webhook → Validate → Create Job → Save Media → Queue Push → Response
### ➡️ Next (방향만)
- DB 테이블 실제 생성 (VPS Postgres)
- n8n Producer 워크플로우 구현
- 씨덴스 API 키 확보 + 연동 테스트
### 📁 Files / Links
- ao-pipeline/CLAUDE.md, HANDOFF.md, PROGRESS.md
- ao-pipeline/docs/01~05

## 2026-03-05 (2차)
### ✅ Done
- [x] 통합 스펙(AO_영상자동화_통합스펙.md) 기반 docs 전면 업데이트
- [x] CLAUDE.md — 기술 스택 교체 (Creatomate/Replicate/ElevenLabs/Supabase)
- [x] docs/01 — 아키텍처 전면 수정 (9탭 UI, 개발 우선순위 포함)
- [x] docs/02 — DB 스키마 수정 (Supabase + 7개 테이블)
- [x] docs/03 — 씨덴스 → 멀티 API 연동 스펙으로 교체
- [x] docs/04 — Producer + Worker 워크플로우 설계 통합
- [x] docs/05 — 입력 스키마 업데이트 (template_id, 파생 필드 추가)
### 📌 Result
- 씨덴스 단독 → Creatomate(영상) + Replicate(이미지) + ElevenLabs(TTS) 조합으로 전환
- DB: n8n-postgres → Supabase (Storage/Auth 포함)
- 프론트: Next.js + Tailwind + shadcn/ui (9탭 관리 UI)
### ➡️ Next (방향만)
- Supabase 프로젝트 생성 + DB 테이블 생성
- Next.js 프론트 초기화
- n8n Producer 워크플로우 구현
### 📁 Files / Links
- CLAUDE.md, HANDOFF.md, PROGRESS.md
- docs/01~05 (전면 수정), docs/03-api-integration.md (신규)

## 2026-03-05 (3차)
### ✅ Done
- [x] DB 테이블 생성 (VPS n8n-postgres, 7개 테이블 + 인덱스 + 트리거)
- [x] n8n Producer/Worker 워크플로우 import
- [x] Postgres credential 생성 (API, ID: 4W3WKJLsJKa9hVAA)
- [x] Producer(1개) + Worker(6개) Postgres 노드에 크리덴셜 연결
- [x] Worker activate → Producer activate
- [x] Producer 웹훅 테스트 성공 (job_id 반환 + DB queued→processing 확인)
### 📌 Result
- Producer: XV5shW265ht59MTD (active)
- Worker: FHYohZccExR24Uha (active)
- 테스트 Job: 032ae279-5ebf-4ee0-a917-980f3b7dd682 (processing)
### ➡️ Next (방향만)
- 외부 API 키 설정 (Replicate, ElevenLabs, Creatomate, YouTube OAuth)
- Worker 풀 파이프라인 테스트
- Next.js 프론트 초기화
### 📁 Files / Links
- n8n/ao_producer.json, n8n/ao_worker.json
- supabase/ao_supabase_init.sql

## 2026-03-05 (4차)
### ✅ Done
- [x] 외부 API 크리덴셜 3건 생성 (n8n API)
  - Replicate API: iG2Q9pXtGuE2xdoS
  - KieAI TTS: OipYAEtrzhD1lJmL
  - Creatomate API: 7uzM44eLOitv8ubQ
- [x] Worker 워크플로우 5개 노드에 크리덴셜 연결
  - 이미지 생성 (Replicate Flux Pro) + 폴링 → Replicate
  - TTS 생성 → KieAI TTS + URL 변경 (ElevenLabs → kie.ai)
  - 영상 렌더링 (Creatomate) + 폴링 → Creatomate
- [x] Worker activate 확인
- [x] 각 API 연결 테스트 성공
  - Replicate: 200 (모델 정보 반환)
  - kie.ai TTS: 200 (taskId 반환, Bearer auth)
  - Creatomate: 400 (인증 통과, template_id 요구 — 정상)
### 📌 Result
- Worker 외부 API 3건 연결 완료, TTS 엔드포인트 kie.ai로 교체
- 남은 크리덴셜: Claude API (번역), YouTube OAuth (업로드)
### ➡️ Next (방향만)
- Claude API 크리덴셜 + 번역 노드 연결
- YouTube OAuth 설정
- Worker 풀 파이프라인 테스트
### 📁 Files / Links
- n8n/ao_worker.json (업데이트)

## 2026-03-05 (이미지 노드 교체)
### ✅ Done
- [x] 이미지 생성 노드 Replicate Flux Pro → kie.ai Nano Banana Pro 교체
- [x] 이미지 폴링 노드: fetch → this.helpers.httpRequest 수정
- [x] VPS 환경변수 추가 (KIEAI_API_KEY, CREATOMATE_API_KEY, N8N_BLOCK_ENV_ACCESS_IN_NODE=false)
- [x] 폴링 코드 $credentials → $env 변경
- [x] 파이프라인 테스트: 번역(Claude) ✅ → 이미지(kie.ai) ✅ → TTS(kie.ai) ✅ → Creatomate ❌
### 📌 Result
- 이미지 생성 성공 (kie.ai nano-banana-pro, ~27초)
- TTS 생성 성공 (kie.ai)
- Creatomate 실패: template_id 미설정 (빈 템플릿만 존재)
### ➡️ Next (방향만)
- Creatomate 쇼츠 템플릿 생성
- 풀 파이프라인 재테스트
### 📁 Files / Links
- n8n/ao_worker.json (이미지 노드 교체)
- /docker/n8n/docker-compose.yml (env vars 추가)

## 2026-03-05 (5차)
### ✅ Done
- [x] Claude API 크리덴셜 생성 (mr2FTmB2pmyvlbWK) + 번역 노드 연결
- [x] Claude API 테스트 성공 ("안녕하세요 반갑습니다 환영합니다")
- [x] YouTube OAuth2 크리덴셜 생성 (FHvjDOGBtI0zvyFA)
  - Client ID: 481347496295-...apps.googleusercontent.com
  - Redirect URI: https://n8n.srv1345711.hstgr.cloud/rest/oauth2-credential/callback
- [x] Worker 업로드 노드에 YouTube OAuth2 연결
### 📌 Result
- 외부 API 크리덴셜 5건 전체 생성/노드 연결 완료
- YouTube OAuth는 브라우저 인증 필요 (n8n 웹 에디터 > Credentials > Sign in with Google)
### ➡️ Next (방향만)
- YouTube OAuth 브라우저 인증
- Worker 풀 파이프라인 테스트
- Next.js 프론트 초기화
### 📁 Files / Links
- n8n/ao_worker.json (업데이트)

## 2026-03-06
### ✅ Done
- [x] Worker 멀티씬 순차 처리 구조 완성 (process-clips → 씬별 Seedance + TTS 통합)
- [x] include_audio 분기 구현 (true: Seedance generate_audio / false: 영상만 + ElevenLabs TTS)
- [x] Creatomate render-video: HTTP Request → Code 노드 변환 (동적 source elements)
- [x] Producer 검증 코드 업데이트 (include_audio, duration 4/8 자동 보정)
- [x] n8n publish 시스템 문제 해결 (activeVersionId DB 직접 갱신)
- [x] /webhook/ao-produce 웹훅 정상 응답 확인
- [x] 1씬 파이프라인 전체 테스트 성공 (번역→Seedance→TTS→Creatomate 합성)
### 🔁 Tried
- n8n CLI import → activeVersionId 미갱신 문제 발견 → DB 직접 갱신으로 해결
- Seedance duration "5" 불허 발견 → "4"/"8"만 허용으로 수정
- Unsplash 리다이렉트 URL → kie.ai 거부 → 이미지 실패 시 텍스트 전용 재시도 로직 추가
- Creatomate jsonBody IIFE 구문 → n8n expression 미지원 → Code 노드로 변환
### 📌 Result
- Worker 19 노드 (이전 23 → 4개 삭제), 깔끔한 멀티씬 파이프라인
- 테스트 job b61c6535: Seedance(4초)→TTS→Creatomate 합성 성공, rendered_video_url 확인
- YouTube 업로드: OAuth 토큰 만료로 실패 (코드 문제 아님, 수동 재인증 필요)
### ➡️ Next (방향만)
- YouTube OAuth 재인증
- Next.js 웹앱 초기화
- 멀티씬 2+ 테스트
### 📁 Files / Links
- n8n/ao_worker.json (멀티씬 구조)
- n8n/ao_producer.json (include_audio 지원)

## 2026-03-06 (2차)
### ✅ Done
- [x] YouTube 업로드 Code 노드 전면 수정
  - n8n OAuth 크리덴셜 → 환경변수 직접 OAuth token refresh
  - this.helpers.httpRequest EPIPE → Node.js native https 모듈로 PUT 업로드
  - VPS 환경변수 추가: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
- [x] 멀티씬 2씬 E2E 테스트 성공 (번역→Seedance→TTS→Creatomate→YouTube)
- [x] YouTube 업로드 재테스트 성공 (제목 변경 확인)
  - 테스트 영상 1: "AO 테스트" (job 0a552f9f)
  - 테스트 영상 2: "AO 파이프라인 테스트 2" (ID: HeYLrBD3pmo, curl 직접 업로드)
### 🔁 Tried
- n8n HTTP Request + googleOAuth2Api → Code 노드에서 토큰 주입 안됨 → 환경변수 방식으로 전환
- this.helpers.httpRequest 바이너리 PUT → write EPIPE → native https 모듈로 해결
### 📌 Result
- 전체 E2E 파이프라인 완성 (입력→번역→Seedance→TTS→Creatomate→YouTube)
- YouTube 업로드 안정적 동작 확인 (2회 연속 성공)
### ➡️ Next (방향만)
- Next.js 웹앱 초기화
- mark-uploaded DB 자동 업데이트 확인
### 📁 Files / Links
- n8n/ao_worker.json (YouTube Code 노드 수정)

## 2026-03-06 (3차)
### ✅ Done
- [x] DB: jobs 테이블에 production_id 컬럼 추가
- [x] Producer: productionId 입력 → production_id로 저장, 응답에 포함
- [x] Worker: 웹앱 콜백 (성공) 노드 추가 — 상태→uploaded 후 POST 콜백
- [x] Worker: 웹앱 콜백 (실패) 노드 추가 — 재시도/실패 후 POST 콜백
- [x] VPS: WEBAPP_CALLBACK_URL 환경변수 추가 (https://api-n8n.xn--9g4bn4fm2bl2mb9f.com)
- [x] n8n 배포 완료 (Producer + Worker)
### 📌 Result
- 콜백 body (성공): { productionId, status: 'uploaded', youtubeVideoId, youtubeUrl, renderedVideoUrl, jobId }
- 콜백 body (실패): { productionId, status: 'failed'|'queued', error, retryCount, jobId }
- production_id 없으면 콜백 스킵 (기존 테스트 job 호환)
### ➡️ Next (방향만)
- 프론트에서 productionId 포함 요청 E2E 테스트
### 📁 Files / Links
- n8n/ao_worker.json (콜백 노드 2개 추가)
- n8n/ao_producer.json (production_id 저장)

## 2026-03-06 (4차)
### ✅ Done
- [x] Producer 입력값 검증: clips[] → files[] 구조 변경
  - files[].type (image/video), files[].url, files[].vision_analysis, files[].video_analysis, files[].use_directly
  - 하위 호환: 기존 clips[] payload도 files[]로 자동 변환
- [x] Worker AO 프롬프트 조립: 모든 파일의 분석 결과를 프롬프트에 반영 (유/무 관계없이)
  - 최종 프롬프트 = [분석 결과들] + P1 원문 (100% 보존)
- [x] Worker 멀티씬 순차 처리: files[] + use_directly 분기
  - use_directly=true → Seedance에 이미지 직접 전달
  - use_directly=false → 분석만 프롬프트에 반영, Seedance에 미전달
  - include_audio/scene_prompt 제거 (메인 P1로 통합)
- [x] VPS 배포 완료 (Producer + Worker active)
### 📌 Result
- 통합 업로드 구조 대응 완료
- P1 원문 100% 보존 + 분석 결과 자동 반영
### ➡️ Next (방향만)
- 프론트에서 files[] payload E2E 테스트
### 📁 Files / Links
- n8n/ao_worker.json (assemble-prompt + process-clips 수정)
- n8n/ao_producer.json (입력값 검증 수정)

## 2026-03-06 (5차)
### ✅ Done
- [x] Producer: prompt_p1 필수 → optional 변경
- [x] Producer: 파일X+프롬프트X 에러 검증 추가
- [x] Worker assemble-prompt: P1 없으면 topic+keywords+분석결과로 자동 프롬프트 생성
- [x] Worker process-clips: 파일 없으면 text_only 씬으로 프롬프트 전용 영상 생성
- [x] prompt_auto_generated 플래그 추가 (디버깅용)
- [x] VPS 배포 완료 (Producer + Worker active)
### 📌 Result
- 4케이스 분기 완성:
  1. 파일O + P1O → 분석결과 + P1 100% 보존
  2. 파일O + P1X → 분석결과 + 자동 프롬프트
  3. 파일X + P1O → P1만으로 text_only 씬 생성
  4. 파일X + P1X → 에러 반환
- P1 있을 때 100% 보존 원칙 유지
### ➡️ Next (방향만)
- 4케이스 E2E 테스트
- 프론트 UI 구조 변경 (web 워크트리)
### 📁 Files / Links
- n8n/ao_worker.json (assemble-prompt + process-clips 수정)
- n8n/ao_producer.json (prompt_p1 optional + 4케이스 검증)

## 2026-03-06 (슬라이드쇼 모드)
### ✅ Done
- [x] Producer: production_mode (ai_video/slideshow) + slide_duration 필드 추가
- [x] Producer: slideshow 모드 시 이미지 최소 1장 검증
- [x] Worker process-clips: slideshow 분기 — Kling 스킵, 이미지 URL + TTS 수집
- [x] Worker render-video: slideshow 분기 — 이미지 슬라이드 + TTS + 자막 Creatomate 렌더
  - scale 애니메이션 (100%→120%), Noto Sans KR 자막, 반투명 배경
- [x] DB: jobs 테이블에 production_mode, slide_duration 컬럼 추가
- [x] VPS 배포 완료 (Producer + Worker active)
### 📌 Result
- production_mode 분기 완성 (ai_video: 기존 Kling 흐름 / slideshow: 이미지→Creatomate 직접)
- 기존 ai_video 코드 변경 없음
### ➡️ Next (방향만)
- 슬라이드쇼 모드 E2E 테스트
- Kling AI E2E 테스트
### 📁 Files / Links
- n8n/ao_worker.json (process-clips + render-video 슬라이드쇼 분기)
- n8n/ao_producer.json (production_mode + slide_duration)

## 2026-03-06 (전체 파이프라인 개편)
### ✅ Done
- [x] Producer: use_mode(direct/generate/analysis_only), generated_images, auto_prompt 필드 추가
- [x] Producer: INSERT 쿼리에 generated_images 컬럼 추가
- [x] Worker process-clips: use_mode별 이미지 처리 (direct/generate/analysis_only)
  - generate: vision_analysis 기반 kie.ai 이미지 생성
  - analysis_only: auto_prompt 기반 kie.ai 이미지 생성
- [x] Worker process-clips: generated_images 합류 지원
- [x] Worker process-clips: TTS를 kie.ai (ElevenLabs multilingual v2)로 통합
  - 자막 타이밍: 문장 분리 + 글자수 비율 배분
- [x] Worker render-video: ai_video도 NCA FFmpeg로 변경 (Kling 영상 + TTS + 자막 + BGM + SFX)
- [x] Worker render-video: ensureExtension 함수 추가 (NCA URL 확장자 필수)
- [x] Worker render-video: URL 클래스 미사용 (n8n Task Runner 제한)
- [x] Worker render-video: -shortest → -t 명시적 시간 (NCA API 호환)
- [x] YouTube 업로드 일시 비활성화 (나중에 활성화)
- [x] 기존 Creatomate/Seedance 코드 비활성화(보존)
- [x] VPS 배포 완료 + E2E 테스트 성공
### 🔁 Tried
- NCA FFmpeg 500: picsum URL에 확장자 없음 → ensureExtension 추가
- NCA FFmpeg 500: URL 클래스 미사용 오류 → 문자열 파싱으로 교체
- NCA FFmpeg 500: -shortest argument 빈값 → -t 명시적 시간으로 교체
### 📌 Result
- 슬라이드쇼 E2E 성공: Job 599c3af3 → uploaded ✅ (이미지 3장 + TTS + 자막 + BGM + SFX)
- 영상화 E2E 성공: Job c1ea1a83 → uploaded ✅ (Kling AI + TTS + 자막 + BGM + SFX)
- 4시나리오 분기 구조 완성 (use_mode + generated_images)
- YouTube 업로드 일시 비활성화 (require('https') 차단 미해결)
### ➡️ Next (방향만)
- YouTube 업로드 활성화
- use_mode generate/analysis_only E2E 테스트
- 프론트 웹앱 연동
### 📁 Files / Links
- n8n/ao_worker.json (process-clips + render-video + poll-render + YouTube 업로드 전면 수정)
- n8n/ao_producer.json (use_mode + generated_images + auto_prompt)

## 2026-03-06 (이전: 슬라이드쇼 edge-tts + NCA FFmpeg)
### ✅ Done
- [x] Worker process-clips: 슬라이드쇼 TTS를 kie.ai → edge-tts 교체
  - POST http://172.17.0.1:5100/tts (voice_id, emotion, tempo)
  - 반환: audio_url, duration_sec, timestamps[] (자막 타이밍)
  - 이미지 표시 시간 = 나레이션 길이 / 이미지 수 (자동 계산)
- [x] Worker render-video: 슬라이드쇼 Creatomate → NCA FFmpeg 교체
  - POST http://76.13.182.180:8080/v1/ffmpeg/compose
  - filter_complex: scale+concat, amix(TTS:BGM:SFX = 1:1:0.8), drawtext 자막
  - BGM 루프 + fade-out, SFX 전환음 (이미지 전환 시점)
- [x] Worker poll-render: NCA 응답 시 Creatomate 폴링 스킵 (early return)
- [x] VPS 배포 완료 (Producer + Worker active)
- [x] 슬라이드쇼 E2E 테스트: 렌더링 성공 ✅
### 📌 Result
- 테스트 Job 79495ae0: edge-tts + NCA FFmpeg → rendered_video_url 생성 성공
- YouTube 업로드에서 멈춤 (require('https') 차단 — 기존 알려진 이슈)
- onca 방식 (edge-tts + FFmpeg) 성공적으로 arubto에 이식
### ➡️ Next (방향만)
- YouTube 업로드 require('https') 해결
- 전체 E2E 완성 (렌더링→업로드)
### 📁 Files / Links
- n8n/ao_worker.json (process-clips + render-video + poll-render 수정)

## 2026-03-06 (Kling AI 연동)
### ✅ Done
- [x] Worker process-clips: Seedance → Kling 3.0 교체 (kling-3.0/video)
  - N이미지 → 영상 1개 직접 생성 (멀티씬 Creatomate 합성 불필요)
  - image_urls 최대 2장, duration 3~15초
  - Seedance 코드 주석으로 보존 (롤백용)
- [x] Producer: clip_duration 검증 4/8 → 3~15 범위 보정으로 변경
- [x] VPS 배포 완료 (Producer + Worker active)
### 📌 Result
- Kling 3.0으로 단일 API 호출로 영상 생성 (이전: Seedance 씬별 + Creatomate 합성)
- workflow_history PK 컬럼명: versionId (id 아님) 확인
### ➡️ Next (방향만)
- Kling AI E2E 테스트 (이미지 2장 → 영상 1개)
- 4케이스 프롬프트 분기 E2E 테스트
### 📁 Files / Links
- n8n/ao_worker.json (process-clips Kling 3.0 교체)
- n8n/ao_producer.json (duration 검증 변경)

## 2026-03-06 (6차)
### ✅ Done
- [x] 운영 시스템 구축 (INIT 프롬프트 적용)
- [x] CLAUDE.md — 새 형식으로 병합 (기존 AO 내용 보존 + 세션 시작 루틴/완료 체크/브리핑 형식 추가)
- [x] HANDOFF.md — Last Run 형식 보완 (커맨드/결과/위치/Last Commit)
- [x] PROGRESS.md — 참조 노트 추가 (Next Actions 정답은 HANDOFF)
- [x] docs/ 7개 파일 생성/업데이트 (01~07, AO Pipeline 맞춤)
- [x] docs/06 — AO 프로젝트 에러 패턴 3건 추가 (activeVersionId/duration/리다이렉트 URL)
- [x] scripts/quality-check.sh 확인 (이미 존재, PASS)
- [x] settings.json.sample 확인 (이미 존재)
- [x] .claude/commands/start.md 확인 (이미 존재)
### 📌 Result
- 운영 시스템 전체 구축 완료 (기존 기록 100% 보존)
- quality-check.sh PASS
### ➡️ Next (방향만)
- 4케이스 E2E 테스트
### 📁 Files / Links
- CLAUDE.md, HANDOFF.md, PROGRESS.md (형식 병합)
- docs/01~07 (신규/업데이트)

## 2026-03-06 (이미지 생성 웹훅)
### Done
- [x] AO Image Generator 워크플로우 신규 생성 (ID: d5b35fb7f1724e448)
- [x] 웹훅 엔드포인트: POST /webhook/ao-generate-image
- [x] Whisk 방식 3슬롯 구조 (subject/scene/style)
  - 각 슬롯: url, vision_analysis, use (true/false)
  - 슬롯별 프롬프트 자동 합성
- [x] kie.ai nano-banana-pro 이미지 생성 (1~3장)
- [x] MinIO 저장: arubto/generated/{timestamp}_{index}.jpg
- [x] MinIO anonymous upload 정책 설정 (generated/ prefix)
- [x] VPS 배포 완료 + E2E 테스트 성공
### Result
- 테스트: /webhook/ao-generate-image → 3장 생성 → MinIO arubto/generated/ 저장 확인
- 응답: { success, count, images: [MinIO URLs], prompt, aspect_ratio, slots_used }
- 워크플로우 구조: Webhook → Code(이미지 생성) → respondToWebhook
### Next (방향만)
- 프론트 웹앱에서 이미지 생성 웹훅 연동
- generated_images를 영상 제작 파이프라인에 전달 E2E
### Files / Links
- n8n/ao_image_generator.json (신규)

## 2026-03-06 (aspect_ratio 분기)
### Done
- [x] Producer: aspect_ratio 필드 추가 (기본값 9:16, 허용: 9:16/16:9)
- [x] Producer: DB INSERT에 aspect_ratio 컬럼 추가
- [x] Worker assemble-prompt: ASPECT_RATIO 하드코딩 → job.aspect_ratio 동적 참조
- [x] Worker process-clips: generateImage + Kling AI aspect_ratio 동적화
- [x] Worker render-video: slideshow/ai_video NCA FFmpeg 해상도 동적화
  - 9:16 → 1080x1920, 16:9 → 1920x1080
- [x] DB: jobs 테이블 aspect_ratio 컬럼 추가
- [x] NCA toolkit GUNICORN_TIMEOUT=600 설정 (worker timeout 방지)
- [x] VPS 배포 + E2E 테스트 성공
### Result
- 9:16 Job 8c75155b → uploaded ✅ (슬라이드쇼 세로)
- 16:9 Job ca5f3cbe → uploaded ✅ (슬라이드쇼 가로)
- NCA FFmpeg 9:16/16:9 모두 정상 렌더링 (2~3초)
### Next (방향만)
- 프론트 웹앱 연동
### Files / Links
- n8n/ao_producer.json (aspect_ratio 필드/INSERT)
- n8n/ao_worker.json (assemble-prompt + process-clips + render-video)

## 2026-03-06 (이미지 웹훅 MinIO 버그 수정)
### Done
- [x] MinIO 저장 제거 → kie.ai URL 직접 반환으로 변경
- [x] VPS 배포 + 테스트 성공
### Tried
- n8n httpRequest PUT에 Buffer body → JSON 직렬화 (`{"type":"Buffer","data":[...]}`)
- encoding: 'arraybuffer', Uint8Array 변환 등 시도 → 모두 실패
- NCA code execute API → 404 (해당 엔드포인트 미지원)
### Result
- kie.ai URL 직접 반환으로 변경 (MinIO 저장은 별도 작업 예정)
- n8n Task Runner에서 httpRequest PUT binary body 전송 불가 확인
### Next (방향만)
- MinIO 바이너리 저장 (별도 작업)
### Files / Links
- n8n/ao_image_generator.json (MinIO 저장 제거)

### ✅ Producer 에러 핸들링 수정 (500→400)
- 증상: ao-produce 웹훅 검증 실패 시 HTTP 500 반환
- 원인: Code 노드 throw → n8n 전체 실행 실패 → 500. "에러 핸들러" 노드는 고립(미연결)
- 수정:
  - 입력값 검증 Code: try-catch 래핑 → 에러 시 `{ error: true, message }` 반환
  - IF 노드 "검증 결과 분기" 추가: error=true → 400 응답 / false → Job 생성
  - 불필요한 stopAndError "에러 핸들러" 노드 제거
- 테스트: 검증 실패 → 400 + 에러 메시지, 정상 요청 → 200 + job_id
### Files / Links
- n8n/ao_producer.json (에러 핸들링 수정)

## 2026-03-06 (Worker 대규모 개선)
### ✅ Done
- [x] 나레이션 자동생성 추가 (Claude API)
  - 우선순위: narration_script(직접입력) > prompt_p1(Claude생성) > topic(Claude생성)
  - 슬라이드쇼/ai_video 모두 적용
  - topic+keywords+category 전부 합쳐서 컨텍스트 제공
- [x] productionMode 우선순위 수정
  - job.production_mode 명시적 설정 우선 (hasDirect가 override하던 버그 수정)
- [x] 중간 콜백 노드 3개 추가 (웹앱 5분 타임아웃 방지)
  - cb-processing: 작업 시작 시
  - cb-rendering: 렌더링 시작 시
  - cb-generated: 렌더링 완료 시
- [x] NCA 한글 자막 폰트 설치 (fonts-nanum)
  - 증상: 한글 자막 □□□ 깨짐
  - 수정: docker exec -u root nca-toolkit apt-get install -y fonts-nanum
  - 주의: 컨테이너 재시작 시 사라짐 (영구화 필요)
- [x] 번역 노드 JSON 이스케이프 버그 수정
  - 증상: prompt에 +|, ", 줄바꿸 포함 시 "JSON parameter needs to be valid JSON" 에러
  - 원인: httpRequest 노드 jsonBody 템플릿이 특수문자 미이스케이프
  - 수정: httpRequest → Code 노드로 교체 (JS 객체 body로 안전 전달)
  - 테스트: 특수문자 포함 프롬프트 → 전체 파이프라인 uploaded ✅
- [x] CLAUDE_API_KEY 환경변수 추가 (docker-compose.yml, n8n + worker)
  - docker compose up -d로 재생성 필요 (restart는 env 미적용)
- [x] Producer: narration_script 컬럼 INSERT 추가
### 🔁 Tried
- kie.ai TTS 402 (크레딧 부족) + 간헐적 internal error → 크레딧 충전 + 재시도로 해결
- docker compose restart vs up -d → restart는 환경변수 미적용 확인
### 📌 Result
- Worker 전체 파이프라인 안정화 (번역→나레이션→TTS→이미지→비디오→렌더링→콜백)
- 특수문자 프롬프트 E2E 성공: Job 65ae2666 → uploaded ✅
### ➡️ Next (방향만)
- 프론트 웹앱 연동
- NCA 한글 폰트 영구화
### 📁 Files / Links
- n8n/ao_worker.json (나레이션+콜백+번역 노드 수정)
- n8n/ao_producer.json (narration_script INSERT)

## 2026-03-07
### ✅ Done
- [x] DB: jobs 테이블에 prompt_hash/duration/strict_mode/verify_mode 컬럼 추가 (ALTER TABLE)
- [x] Producer: prompt_p1 필수화, topic/keywords/category 선택으로 변경 (저장/표시 전용)
- [x] Producer: duration 허용값 검증 (30/40/50/60/90/120/150/180)
- [x] Producer: prompt_hash(FNV-1a) 생성 + DB 저장
- [x] Producer: strict_mode/verify_mode 파라미터 추가
- [x] Worker: Last-Edit Priority — prompt_p1 단일 소스, 슬롯 치환({TOPIC} 등) 제거
- [x] Worker: Prompt Lock — prompt_hash 비교, 불일치 시 prompt_lock_valid=false
- [x] Worker: Length Gate — target_duration+1초 버퍼, clip_count 재계산, strict_mode 분기
- [x] Worker: verify_mode — output_hash를 mark-generated에서 job_logs에 INSERT
- [x] docs/05-input-schema.md — Prompt Lock/Last-Edit Priority/Length Gate/verify_mode 문서화
- [x] docs/06-error-patterns.md — LENGTH_GATE_BLOCKED/Prompt Lock 불일치 패턴 추가
- [x] supabase/ao_supabase_init.sql — CREATE TABLE + ALTER TABLE 양쪽 반영
- [x] 미사용 레거시 파일 57개 일괄 정리 (63,877줄 삭제)
### 🧪 Test
- 30초 케이스 (job 874989a6): duration=30, strict_mode=false → length_gate_status=corrected, total_duration=19.1s → uploaded ✅
- 60초 케이스 (job c0a3dde4): duration=60, strict_mode=true → length_gate_status=pass, total_duration=39.8s → uploaded ✅
- 잘못된 duration(45) → 400 에러 반환 ✅
- prompt_p1 누락 → 400 에러 반환 ✅
- prompt_hash DB 저장 확인 ✅
- verify_mode output_hash job_logs 기록 확인 ✅
### 📌 Result
- P0 뼈대 3개 기능 모두 구현 완료
- Producer 입력 계약 확정: prompt_p1 필수, topic/keywords/category 선택
- n8n Code 노드에서 crypto 모듈 미지원 → FNV-1a 해시 대체
### ➡️ Next (방향만)
- 프론트 웹앱 연동
- Prompt Lock 불일치 시 실제 재생성 플로우 구현 (현재는 감지만)
### 📁 Files / Links
- n8n/ao_producer.json, n8n/ao_worker.json
- supabase/ao_supabase_init.sql
- docs/05-input-schema.md, docs/06-error-patterns.md
- HANDOFF.md, PROGRESS.md

## 2026-03-07 (2차)
### ✅ Done
- [x] Prompt Lock IF 분기: assemble-prompt 후 IF 노드("Prompt Lock 확인") 추가
- [x] Prompt Lock 재생성 노드: prompt_lock_valid=false 시 최신 prompt_p1로 재조립
- [x] 렌더 전 2차 확인: "렌더 전 Prompt 확인"(Postgres) + "렌더 Lock 확인"(Code) 노드 추가
- [x] 나레이션 분량 지시: generateNarration에 target_duration 기반 글자수(4.5자/초) 전달
- [x] TTS 길이 부족 시 나레이션 재생성 1회 시도 (짧으면 그대로 진행 + job_logs 기록)
- [x] Length Gate 통과 기준 개선: strict=target±1초, soft=target-3초~target+1초
- [x] clip_count 보정: 짧으면 클립 반복(corrected_short), 길면 분할(corrected_long)
- [x] length_gate_status 세분화: corrected_short/corrected_long/under_soft/over_soft/blocked_short/blocked_long
- [x] mark-generated에 prompt_hash 갱신 + prompt_lock_action/length_gate_log 기록
### 🧪 Test
- 30초 케이스 (job 7c1db8f4): duration=30, strict=false → total_duration=31.3초, over_soft → uploaded ✅
  - 이전(P0): 19.1초 → 이번: 31.3초 (목표 근처 도달)
- Prompt Lock 재생성: IF 분기 노드 + 재생성 노드 + 렌더 전 재확인 구조 완성
- 잘못된 duration/prompt_p1 누락: 기존 400 에러 유지 확인
### 📌 Result
- 30초 길이 이슈 해결: 나레이션 분량 지시 + 재생성 1회로 목표 근처 도달
- Prompt Lock: 감지만 → 재생성 플로우 연결 완료
- Length Gate: 단방향(초과만) → 양방향(부족+초과) 보정
### ➡️ Next (방향만)
- 프론트 웹앱 연동
### 📁 Files / Links
- n8n/ao_worker.json (4개 노드 추가, 2개 노드 수정)
- docs/05-input-schema.md, docs/06-error-patterns.md
- HANDOFF.md, PROGRESS.md

## 2026-03-07 (Phase 2 완료)
### 🎯 Goal
- engine_type 분기 골격 + narration_style/narration_tone 검증 + SPEC 4조 적용 + E2E 테스트
### ✅ Done
- [x] engine_type 검증: Producer validate-input에 5종 허용값 검증 추가
- [x] engine_type Switch 골격: Producer에 Switch 노드 추가 (5경로+fallback, 모두 공통 합류)
- [x] narration_style 검증: 설명형/스토리형/광고형/감성형 (허용값 외 400 에러)
- [x] narration_tone 검증: 차분하게/흥분되게/유머러스하게/긴박하게 (허용값 외 400 에러)
- [x] Worker generateNarration: narration_style/tone Claude 프롬프트 반영
- [x] Worker generateNarration: topic/keywords/category 참조 제거 (SPEC 4조)
- [x] DB 스키마: engine_type/narration_style/narration_tone 컬럼 추가 (CREATE TABLE + ALTER TABLE)
- [x] E2E 테스트 성공: Job f17e0059 queued → processing → uploaded
- [x] bgm_file_url / sfx_file_url 미구현 확인 → Next Actions에 기록
### 🧪 Test
- E2E: prompt_p1 + duration=30 + narration_style=설명형 + narration_tone=차분하게 → uploaded 성공
- DB 검증: narration_style/narration_tone/engine_type 정상 저장
- 입력 검증: invalid style → 400, invalid tone → 400
### 📌 Result
- Phase 2 기능 구현 완료, E2E 통과
- bgm_file_url / sfx_file_url은 추후 작업으로 분리
### ➡️ Next (방향만)
- 프론트 웹앱 연동
- bgm_file_url / sfx_file_url 필드 추가
### 📁 Files / Links
- n8n/ao_producer.json (validate-input, create-job, Switch 골격)
- n8n/ao_worker.json (generateNarration 수정)
- supabase/ao_supabase_init.sql (3컬럼 추가)
- HANDOFF.md, PROGRESS.md

## 2026-03-07
### ✅ Done
- [x] clip_duration auto 모드 구현 (TTS 실측 기반 Kling duration)
- [x] B-1 버그 수정 — direct 모드 원본 이미지 Kling AI 전달
### 🔁 Tried
- B-1: 코드 흐름 분석 — processFilesByUseMode→allImages→klingInput.image_urls 정상
- B-1: 근본 원인 — Kling API 실패 시 image_urls를 silent fallback으로 삭제하는 retry 로직
### 📌 Result
- clip_duration=0/'auto' → assemble-prompt에서 'auto'로 정규화, TTS→Kling 순서 재배치
- B-1: direct 이미지 별도 추적(directImages), Kling 실패 시 direct 이미지 포함이면 에러 throw
- generated/analysis_only 이미지만 fallback 허용 (기존 동작 유지)
- 출력 추가: clip_duration_mode, actual_clip_duration, direct_image_urls
### ➡️ Next (방향만)
- 프론트 웹앱 연동
- MinIO 이미지 URL 공개 접근 확인 (direct 모드 Kling 접근 필요)
### 📁 Files / Links
- n8n/ao_worker.json (assemble-prompt, process-clips 수정)
- HANDOFF.md, PROGRESS.md

## 2026-03-08 (F-7/F-8/F-9)
### Done
- [x] F-7: buildSubtitleSegments -> buildSubtitleTimings (Claude API 자연 타이밍)
- [x] F-8: auto 모드 totalDuration = max(tts.duration, scene_duration)
- [x] F-9: 효과음 AI 타이밍 + 동적 배치
  - generateSfxTimings 함수: Claude API로 나레이션 구간 분석 -> 최대 5개 SFX 배치 시점 결정
  - process-clips: sfx_timings 출력 추가
  - render-video: hardcoded sfxIdx -> 동적 sfxIndices 배열 (다중 SFX adelay)
  - render-video fallback: sfx_timings 없으면 기존 500ms 단일 SFX
  - mark-generated: job_logs에 tts_duration/scene_duration/total_duration_source/sfx_count 추가
### Scope Limitation
- SFX 파일 AI 생성 보류: kie.ai/fal.ai에 SFX 생성 모델 없음
- 현재: 기존 sfx_ppook.wav를 AI가 결정한 타이밍에 배치
- 향후: SFX 생성 API 확보 시 generateSfxTimings 결과의 description으로 음원 생성 가능
### Next
- VPS 업로드 (ao_worker.json)
- 프론트 웹앱 연동
### Files
- n8n/ao_worker.json (process-clips, render-video, mark-generated 수정)
- HANDOFF.md, PROGRESS.md

## 2026-03-08 (bgm_mode/sfx_mode + F-10)
### Done
- [x] bgm_mode: ai_auto/uploaded/none (enable_bgm 하위 호환)
- [x] sfx_mode: ai_auto/uploaded/combined/none (enable_sfx 하위 호환)
- [x] sfx_file_url: uploaded/combined용 사용자 SFX URL
- [x] render-video: SFX_ACTIVE_URL 분기 (모드별 SFX 소스)
- [x] F-10: matchImageToScene — Claude API vision_analysis + 프롬프트/나레이션 매칭
- [x] image_order=auto: 이미지 2장 이상 시 AI 순서 재배치
- [x] VPS 업로드 + DB 동기화 완료
### Files
- n8n/ao_worker.json (process-clips, render-video 수정)
- HANDOFF.md, PROGRESS.md

## 2026-03-08 (세션 2)
### ✅ Done
- [x] process-clips: kie.ai 402 크레딧 부족 감지 → KIE_CREDIT_INSUFFICIENT throw
- [x] process-clips: 전체 처리 로직 try-catch 래퍼 → 에러 시 error JSON 반환
- [x] render-lock-check: error JSON 감지 → throw → 파이프라인 즉시 중단
- [x] render-video: error passthrough (_input.error === true → 바로 반환)
- [x] upload-youtube: error passthrough (job.error === true → 바로 반환)
- [x] pop-queue: Watchdog SQL 추가 (5분 이상 processing → 자동 failed)
- [x] settings.errorWorkflow: 깨진 템플릿 문자열 클리어 (빈 문자열)
- [x] VPS 배포 + DB nodes/activeVersionId 동기화 + restart 완료
- [x] 수동으로 stuck processing job 2건 정리
### 🔍 Root Cause
- processing 고착 원인: errorWorkflow가 `{{ AO Worker 에러 핸들러 워크플로우 ID }}` 템플릿 문자열로 설정됨 → 실제 ID 아님 → 에러 핸들링 미작동
- kie.ai 402: 크레딧 부족 시 에러를 catch하지 못해 무한 대기
### Files
- n8n/ao_worker.json (process-clips, render-lock-check, render-video, upload-youtube, pop-queue, settings)
- HANDOFF.md, PROGRESS.md

## 2026-03-08 (세션 3)
### ✅ Done
- [x] Watchdog을 pop-queue에서 분리 → 전용 3노드 파이프라인
  - watchdog-check (Postgres): processing > 5분 → failed UPDATE + RETURNING
  - watchdog-callback (Code): 웹앱 콜백 POST (3회 재시도, exponential backoff 1s/2s/4s)
  - watchdog-log (Postgres): 콜백 실패 시 job_logs INSERT
- [x] 흐름 변경: 스케줄 트리거 → watchdog-check → watchdog-callback → watchdog-log → pop-queue
- [x] pop-queue에서 Watchdog SQL 제거 (SELECT만 유지)
- [x] stuck production 3건 수동 콜백 전송 (8b7da108, 0c5673c4, eac34d3b → 200 OK)
- [x] VPS 배포 + DB 동기화 + restart 완료
### Files
- n8n/ao_worker.json (watchdog-check, watchdog-callback, watchdog-log 추가, pop-queue 수정, connections 변경)
- HANDOFF.md, PROGRESS.md
