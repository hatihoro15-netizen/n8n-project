# HANDOFF.md — 현재 상태/진행상황 (항상 전체 Overwrite)

> ✅ 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다. (과거 기록은 PROGRESS.md에 남기고, 여기엔 최신 상태/Next/LastRun/Blockers만 유지)

🔎 INDEX: Current Status | Goal | Next Actions | Last Run Command | Result | Blockers | Known Issues | 변경 파일 | 다음 세션 메시지

---

## A) 상태 요약
- **현재 워크스페이스**: n8n 온카
- **Current Status**: 캡처 파이프라인 추가 완료, 테스트 대기
- **Goal**: 온카 설명형 워크플로우(v16)에 웹사이트 캡처 기능 추가
- **Current Mental Model**: v16 워크플로우에 캡처 3노드 병렬 분기를 추가하고 NCA에서 캡처 이미지를 기존 이미지 슬롯에 병합하는 구조

## B) 환경/의존성
- **서버**: VPS 76.13.182.180 (Hostinger KVM1, Malaysia)
- **Branch**: feature/onca-capture (feature/onca-shortform-v16에서 분기)
- **Environment**: Production (n8n 서버 업로드 완료, 비활성 상태)
- **Runtime/Versions**: n8n (queue-mode), 캡처 서비스 포트 3100
- **Required Secrets**: 없음 (캡처 서비스는 VPS 내부 통신)
- **작업 폴더**: ~/n8n-worktrees/onca-capture/
- **원본 폴더**: ~/n8n-worktrees/onca/ (수정 금지)
- **워크플로우 ID**: 9v1Qc84iI19lQCEx
- **워크플로우 이름**: [온카 스터디] 설명형 숏츠 - 캡처 v16
- **노드 수**: 45개
- **캡처 서비스**: POST http://76.13.182.180:3100/capture (헬스체크: GET :3100/health)

## C) 마지막 실행 기록 (필수)
- **Last Run Command**: n8n 서버 업로드 (워크플로우 ID: 9v1Qc84iI19lQCEx)
- **Result**: 업로드 성공, 비활성 상태 (테스트 후 수동 활성화)
- **실행 위치**: VPS (https://n8n.srv1345711.hstgr.cloud)

## D) 완료/미완료

### Done ✅
- [x] 복사본 생성 + 워크플로우 이름 변경
- [x] 아럽토 캡처 노드 분석 + 삽입 계획 수립
- [x] 캡처 파이프라인 추가 (3개 노드 + 프롬프트/파싱/NCA 수정)
- [x] 캡처 결과 수집 → NCA 데이터 준비 connection 추가
- [x] capture_targets AI 생성 제거 → 고정 빈 배열로 변경
- [x] 캡처 타겟 분리 URL 테이블 추가 (13개 subtopic)
- [x] n8n 서버 업로드 완료
- [x] 콘텐츠 파싱: 날린 금지어 카테고리1 전용으로 범위 축소
- [x] 4파일 체계 정비 (CLAUDE/HANDOFF/process/PROGRESS)

### In Progress 🔧
- [ ] 없음

### Next Actions ➡️ (우선순위 1~3)
1. [ ] 워크플로우 실제 테스트 실행 (비활성 → 수동 실행)
2. [ ] 캡처 결과 확인 및 NCA 이미지 병합 검증
3. [ ] 테스트 통과 후 워크플로우 활성화

## E) Blockers / Issues
- **Blockers**: 없음
- **Known Issues**: 없음
- **롤백 필요 시**: claude-tools/onca_shortform_v16.json (원본 복사본)으로 Import 복원

## F) 변경 파일
| 파일 | 역할 |
|------|------|
| claude-tools/onca_shortform_v16.json | 원본 복사본 (참고용) |
| claude-tools/onca_shortform_v16_capture.json | 캡처 기능 추가 작업본 |

**추가된 노드 (3개):**
캡처 타겟 분리(Code v2) → 캡처 요청 v2(HTTP Request v4.3) → 캡처 결과 수집(Code v2)

**수정된 노드 (3개):**
프롬프트 생성 / 콘텐츠 파싱 / NCA 데이터 준비

**연결 구조:**
시트 기록 → (병렬 3분기) TTS / 세그먼트 / 캡처 → NCA 데이터 준비

**캡처 이미지 병용 로직:** captureResults > 0이면 기존 image 슬롯 마지막 N개를 캡처로 대체, 없으면 기존 유지, try-catch 폴백

**주의사항:** 원본 폴더 수정 금지 / top-level+activeVersion 양쪽 수정 완료 / 병렬 분기라 기존 경로 영향 없음

## G) 다음 세션 시작용 메시지 (복붙)
> 온카 캡처 v16: 캡처 파이프라인 3노드 추가 + NCA 병합 로직 완료, n8n 서버 업로드됨(비활성). 다음 단계는 워크플로우 실제 테스트 실행 및 캡처 이미지 병합 검증.
