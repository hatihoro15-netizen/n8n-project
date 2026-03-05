# PROGRESS.md — 진행 일지

> ❌ 날짜별 보고서는 append만(삭제/overwrite 금지).
> ✅ 상단 "현재 요약" 섹션만 매 세션 overwrite 가능.
> ✅ Next Actions 정답은 HANDOFF.md에. 여기엔 방향/메모만.

---

## 현재 요약 (이 섹션만 overwrite 가능)
- 마지막 업데이트: 2026-03-06
- 현재 상태(1줄): 운영 시스템 구축 완료 + 프롬프트 자동 생성 로직 추가
- 진행중 작업: 4케이스 E2E 테스트
- 최근 완료: 운영 시스템(docs/scripts/commands) 구축, 프롬프트 자동 생성
- 주의사항: n8n publish 시스템 주의(배포 절차 HANDOFF.md 참조)

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
