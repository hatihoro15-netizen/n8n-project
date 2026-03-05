# /start — 새 세션 시작 루틴

1) CLAUDE.md 읽기 (작업 규칙)
2) HANDOFF.md 읽기 (오늘 할 일 / LastRun / Blockers 스냅샷)
3) PROGRESS.md 읽기 (최근 이력 / 마지막 업데이트)
4) 작업 유형에 따라 필요한 docs만 열기
5) git status 확인
6) (선택) scripts/quality-check.sh 실행

## 출력 (세션 첫 응답에 반드시 포함)
- 📝 현재 상태 (1줄)
- 🎯 이번 목표 (1개)
- ➡️ Next Actions Top 3 (HANDOFF 기준)
- ⚠️ Blockers (HANDOFF 기준)
- 📌 주의 규칙 Top 3 (CLAUDE / docs 기준)

> ⚠️ 위 출력 전에는 어떤 작업도 시작하지 마.
