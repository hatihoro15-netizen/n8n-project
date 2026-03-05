# 05-quality-check.md — 품질 검사 규칙/체크리스트

## 코드 품질 기준
- JS/JSON 스탠다드 준수 / 모든 함수 JSDoc
- try-catch 필수 / 하드코딩 금지 (IP/비밀번호/토큰)
- 단일 책임 / 의미 있는 네이밍 / 복잡 로직 주석

## scripts/quality-check.sh 검사 항목
- JSON 문법 검사
- JS 문법 검사 (node --check)
- TS 문법 검사 (tsconfig+tsc 있을 때만 tsc --noEmit, 없으면 skip)
- Python 문법 검사 (py_compile)
- 하드코딩 패턴 검사 (IP, password류 키워드)
- 필수 파일 존재 검사

## 완료 조건 체크
| 항목 | 상태 |
|---|---|
| CLAUDE.md | ✅/❌ |
| HANDOFF.md | ✅/❌ |
| PROGRESS.md | ✅/❌ |
| docs/ 7개 | ✅/❌ |
| scripts/quality-check.sh | ✅/❌ |
| settings.json.sample | ✅/❌ |
| .claude/commands/start.md | ✅/❌ |
| quality-check.sh PASS | ✅/❌ |
