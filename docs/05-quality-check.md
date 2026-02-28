# 품질 검사 규칙

## 자동 검사 (scripts/quality-check.sh)
| 검사 항목 | 대상 | 기준 |
|-----------|------|------|
| JSON 문법 | *.json | python3 -m json.tool 통과 |
| JavaScript 문법 | *.js | node --check 통과 |
| Python 문법 | *.py | python3 -c compile 통과 |
| 하드코딩 탐지 | 전체 파일 | IP 주소, 비밀번호 패턴 없음 |
| 필수 파일 존재 | 프로젝트 루트 | CLAUDE.md, PROGRESS.md, docs/ 존재 |

## 수동 체크리스트

### 워크플로우 JSON 검사
- [ ] 모든 노드에 고유 ID 존재
- [ ] 커넥션에 빠진 연결 없음
- [ ] 크레덴셜 ID가 올바른 값
- [ ] onError 설정이 필요한 노드에 적용됨
- [ ] Wait 노드 대기시간 적절

### 프롬프트 검사
- [ ] 캐릭터 프로필 전문 포함 (축약 금지)
- [ ] 금지어 목록 최신 상태
- [ ] 출력 JSON 형식 명시
- [ ] 턴 구조/화자 순서 정확

### 코드 품질 검사
- [ ] 모든 함수에 JSDoc 존재
- [ ] try-catch 에러 처리 적용
- [ ] 하드코딩 없음 (설정값은 변수/환경변수)
- [ ] 단일 책임 원칙 준수
- [ ] 의미 있는 변수명/함수명

## 검사 실행 방법
```bash
./scripts/quality-check.sh
```
모든 항목 PASS 시에만 커밋 가능.
