# HANDOFF.md — 현재 상태/진행상황 (항상 전체 Overwrite)

> ✅ 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.
> (여기엔 최신 상태/Next/LastRun/Blockers만 유지)

🔎 INDEX: Current Status | Goal | Next Actions | Last Run Command | Result | Blockers | Known Issues | 변경 파일 | 다음 세션 메시지

---

## A) 상태 요약
- **현재 워크스페이스**: 웹앱
- **Current Status**: AI 주제 생성 프롬프트 강화 + 리트라이 로직 추가 완료 (n8n 42노드), 웹앱 executionId 매핑 배포 완료
- **Goal**: 숏폼 자동 생성 워크플로우 v16 안정화 + 웹앱 연동 안정화
- **Current Mental Model**: n8n 워크플로우 에러 핸들링/콜백/카운터 시스템 안정화됨. Gemini 주제 생성 품질 문제 미해결. 웹앱 콜백 API 동작 확인됨.

## B) 환경/의존성
- **서버**: VPS 76.13.182.180 (Hostinger KVM1, Malaysia)
- **Branch**: `feature/onca-shortform-v16`
- **Environment**: Production (n8n self-hosted, queue-mode)
- **Runtime/Versions**: TypeScript / Node.js (Next.js + Fastify + Prisma)
- **n8n URL**: `https://n8n.srv1345711.hstgr.cloud`
- **워크플로우 ID**: `x6xTzHJ9WbUc94ec`
- **Required Secrets**: N8N_API_KEY (값 기재 금지)

## C) 마지막 실행 기록 (필수)
- **Last Run Command**: Webhook POST `/onca-shortform-v16` (웹앱 E2E 테스트)
- **Result**: 실행 #1310 — category 1, subtopic "먹튀 제보와 검증 과정" → Gemini가 "스포츠 승무패 예측" 생성 (소재 무관) → 주제 파싱 통과 (category 1은 금지어 제외) → AI 콘텐츠 생성에서 에러 → 실패 경로 진행
- **실행 위치**: VPS (n8n 서버)

## D) 완료/미완료

### Done ✅
- [x] Webhook + 콜백 시스템 구축 (`f1a620a`)
- [x] 중간 단계 콜백 4개 (`80b9965`)
- [x] v3 종합 패치 머지 (`d3c58d1`)
- [x] 에러 핸들링 7개 경로 완비 (`f6c9608`)
- [x] 콜백 executionId 추가 (`fff8f3b`)
- [x] 웹앱 executionId 매핑 배포 (2026-03-04)
- [x] 주제 파싱 금지어 조기 검증 추가 (2026-03-04)
- [x] 실패 시 카운터 고정 문제 수정 (2026-03-04)
- [x] AI 주제 생성 프롬프트 강화 + 리트라이 판단 노드 추가 (2026-03-04)

### In Progress 🔧
- [ ] Gemini 주제 생성 품질 개선 — 프롬프트 강화 후에도 소재와 무관한 주제 생성 (모델 한계)
- [ ] 에러 준비 노드 `input.error` 문자열 타입 미처리 → "알 수 없는 에러" 폴백 문제

### Next Actions ➡️ (우선순위 1~3)
1. [ ] Gemini 주제 생성 개선: 프롬프트 추가 강화 또는 다른 모델 검토
2. [ ] 에러 준비 노드 에러 메시지 추출 개선
3. [ ] 콜백 API에 status 검증 로직 추가 (현재 Prisma enum만 방어)

## E) Blockers / Issues
- **Blockers**: Gemini가 카테고리/소재와 무관한 주제를 반복 생성 (프롬프트 강화로도 미해결, 모델 한계 가능성)
- **Known Issues**:
  - Gemini API rate limit 시 AI 주제 생성 에러 (연속 webhook 실행 시, #1292)
  - 에러 준비 노드의 `input.error` 문자열 타입 미처리 → "알 수 없는 에러" 폴백
  - 콜백 API에 status 검증 로직 없음 (Prisma enum만 방어)
  - Webhook vs 수동 실행: 웹앱 E2E 연속 호출 시 rate limit 초과 가능 (#1292)
- **롤백 필요 시**: n8n API로 백업 JSON Import, 워크플로우 ID `x6xTzHJ9WbUc94ec`

## F) 변경 파일
- `onca-shortform-v16.json` — 메인 워크플로우 (42노드)
- 웹앱 백엔드: 콜백 API executionId 매핑 (코드 변경 없이 재배포)

## G) 다음 세션 시작용 메시지 (복붙)
> 온카 숏폼 v16 워크플로우 (42노드). 에러 핸들링/콜백/카운터 시스템 안정화 완료. Gemini 주제 생성 품질 문제(소재 무관 주제 반복)가 미해결 blocker. 에러 준비 노드 input.error 문자열 처리도 미수정. 워크스페이스: 웹앱.
