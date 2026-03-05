# 09-file-roles.md — 파일별 역할 (혼용 금지)

## CLAUDE.md
- 최상위 운영 규칙 / 행동 지침
- 수정 시 이유/영향 보고 필수

## HANDOFF.md
- 다음 세션 즉시 실행 스냅샷 (항상 전체 Overwrite)
- 포함: Current Status / Goal / Next Actions(커맨드 포함) / Last Run / Blockers
- Next Actions / Last Run / Blockers의 유일한 정답

## PROGRESS.md
- 진행 일지(히스토리)
- 상단 "현재 요약" 섹션만 매 세션 overwrite 가능
- 날짜별 보고서는 Append only
- 포함: Done / Tried / Result / Next(방향만) / Files
- 기록 금지: 실행 커맨드 정답 (그건 HANDOFF)

## docs/ (참조용 정식 문서)
- 변하지 않는 참조 자료. 수정 시 이유/영향 보고 필수
- 새 에러 패턴 발견 시 docs/06에 즉시 추가

## scripts/
- 자동 검사 도구 (quality-check.sh 등)

## 워크플로우 JSON (*.json)
- n8n 워크플로우 원본/작업본
- 변경 전 Export 백업 필수 / 하드코딩 금지

## 혼용 금지 규칙
- 즉시 실행할 것 → HANDOFF.md
- 작업 일지 → PROGRESS.md
- 운영 규칙 → CLAUDE.md
- 정식 참조 문서 → docs/
- 자동 검사 → scripts/
