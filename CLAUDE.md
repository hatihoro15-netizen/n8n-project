# CLAUDE.md — 운영 지침 (N8 Video Manager)
> ⚠️ 최상위 규칙. 수정 시 이유/영향 먼저 보고.

## 파일 역할
| 파일 | 역할 | 규칙 |
|---|---|---|
| CLAUDE.md | 운영 지침 | 고정 |
| HANDOFF.md | 세션 스냅샷 | 항상 전체 Overwrite |
| PROGRESS.md | 진행 일지 | 상단 요약만 Overwrite / 보고서 Append |
| docs/ | 정식 참조 문서 | 수정 시 보고 |
> Next/LastRun/Blockers 정답 = HANDOFF.md (예외 없음)

## 우선순위: 사용자 지시 > CLAUDE > HANDOFF > PROGRESS/docs

## 프로젝트
- N8 Video Manager / VPS: 76.13.182.180 / n8n: https://n8n.srv1345711.hstgr.cloud
- 워크스페이스: ~/n8n-worktrees/arubto-prompt / 브랜치: feature/arubto-prompt
> ⚠️ 워크스페이스 확정 전 코드/서버 변경 금지

## 세션 시작 루틴 (INIT)
순서: HANDOFF → PROGRESS(요약+최근1개) → 해당 docs만
docs 목차: 01 아키텍처 / 02 인프라 / 03 파일역할 / 04 워크플로우 / 05 품질 / 06 에러 / 07 보고서

첫 응답 브리핑(필수):
📝 현재 상태 / 🎯 목표 / ➡️ Next Top3(HANDOFF) / ⚠️ Blockers / 📌 주의규칙 Top3
> ⚠️ 브리핑 + 계획 출력 전 작업 시작 금지

## 작업 방식
최소변경 / 비밀값 출력·커밋 금지 / 계획 먼저 보고 후 작업 / 막히면 추측 금지

## 완료 체크
- [ ] quality-check.sh PASS / 동작 확인 / git commit
- [ ] HANDOFF Overwrite / PROGRESS 요약 갱신 + 보고서 Append
말미: ✅한일 / 📁파일 / 🧪테스트 / ⚠️이슈 / ➡️다음

## 절대 금지
하드코딩 / 임시방편 / 파일전체교체 / 동시수정 / 커밋없이시작
n8n: API업로드 후 F5필수 / top-level+activeVersion양쪽수정 / $json체인확인 / alwaysOutputData
중단조건: 동작중기능수정 / 파일삭제 / 방법불확실 / 요구사항모호 / 예상외에러
