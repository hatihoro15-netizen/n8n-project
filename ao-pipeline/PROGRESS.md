# PROGRESS.md — 진행 일지

> ❌ 날짜별 보고서는 append만(삭제/overwrite 금지).
> ✅ 상단 "현재 요약" 섹션만 매 세션 overwrite 가능.

---

## 현재 요약 (이 섹션만 overwrite 가능)
- 마지막 업데이트: 2026-03-05
- 현재 상태(1줄): 프로젝트 셋업 + 씨덴스 API 조사 완료
- 진행중 작업: -
- 최근 완료: 초기 셋업, 씨덴스 API 조사, Producer 초안 설계
- 주의사항: 씨덴스 공식 API 미출시 — 서드파티 접근 필요

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
