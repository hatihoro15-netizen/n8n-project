# PROGRESS.md — 진행 일지

> ❌ 날짜별 보고서는 append만(삭제/overwrite 금지).
> ✅ 상단 "현재 요약" 섹션만 매 세션 overwrite 가능.

---

## 현재 요약 (이 섹션만 overwrite 가능)
- 마지막 업데이트: 2026-03-05
- 현재 상태(1줄): 통합 스펙 기반 docs 전면 업데이트 완료
- 진행중 작업: -
- 최근 완료: 통합 스펙 반영 (Creatomate/Replicate/ElevenLabs/Supabase)
- 주의사항: 외부 API 키 미확보, Supabase 프로젝트 미생성

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
