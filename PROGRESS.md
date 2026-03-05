# PROGRESS.md — 진행 일지

> ❌ 날짜별 보고서는 append만(삭제/overwrite 금지).
> ✅ 상단 "현재 요약" 섹션만 매 세션 overwrite 가능.

---

## 현재 요약 (이 섹션만 overwrite 가능)
- 마지막 업데이트: 2026-03-05
- 현재 상태(1줄): Worker 파이프라인 번역→이미지→TTS 성공, Creatomate 템플릿 필요
- 진행중 작업: Creatomate 쇼츠 템플릿 생성
- 최근 완료: 이미지 생성 Replicate→kie.ai 교체, 폴링 코드 수정, 파이프라인 테스트
- 주의사항: Creatomate에 실제 쇼츠 템플릿 미생성 상태

---

## 작업 보고서 (append-only)

(여기서부터 날짜별 append)

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
