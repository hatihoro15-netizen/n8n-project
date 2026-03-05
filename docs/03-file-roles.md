# 03-file-roles.md — 파일별 역할 (혼용 금지)

## 4파일 체계 (핵심)

### CLAUDE.md
- 최상위 운영 규칙 / 행동 지침
- 수정 시 이유/영향 보고 필수

### HANDOFF.md
- **다음 세션 즉시 실행 스냅샷** (항상 전체 Overwrite)
- 포함: Current Status / Goal / Next Actions(커맨드 포함) / Last Run / Blockers
- Next Actions / Last Run / Blockers의 유일한 정답

### process.md
- **정제된 지식베이스** (Append only, 삭제/Overwrite 금지)
- 포함: 컨벤션 / ADR(결정 이유) / 프로젝트 고유 트러블슈팅
- 오염 방지: 단순 문법/오타/일회성 에러 기록 금지

### PROGRESS.md
- **진행 일지(히스토리)**
- **상단 "현재 요약" 섹션만** 매 세션 overwrite 가능
- 날짜별 보고서는 Append only
- 포함: Done / Tried / Result / Next(방향만) / Files
- 기록 금지: 실행 커맨드 정답 (그건 HANDOFF)

## docs/ (참조용 정식 문서)
- 아키텍처/규칙/에러패턴 등 변하지 않는 참조 자료
- 수정 시 이유/영향 보고 필수
- 새 에러 패턴 발견 시 docs/06-error-patterns.md에 즉시 추가

## scripts/
- 자동 검사 도구 (quality-check.sh 등)

## 워크플로우 JSON (*.json)
- n8n 워크플로우 원본/작업본
- 변경 전 Export 백업 필수
- 하드코딩 금지 (ENV/설정 참조)

## 혼용 금지 규칙
- 작업 일지 → PROGRESS.md
- 즉시 실행할 것 → HANDOFF.md
- 재사용 지식/결정 → process.md
- 운영 규칙 → CLAUDE.md
- 정식 참조 문서 → docs/
- 자동 검사 → scripts/
