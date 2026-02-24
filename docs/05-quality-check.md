# 05. 품질 검사 규칙

## 자동 검사 (quality-check.sh)
- 스크립트 위치: `scripts/quality-check.sh`
- 실행 조건: Bash 도구 사용 후 자동 실행 (PostToolUse 훅)
- 프로젝트 디렉토리에서만 실행 (pwd 체크)

### 검사 항목 (5단계)
1. **JSON 문법 검사** - 모든 .json 파일 python3 json.tool 검증
2. **Python 문법 검사** - *.py 파일 syntax 검사 (python3 -c compile)
3. **하드코딩 검사** - IP 주소, 비밀번호 패턴 탐지 (py/js 대상)
4. **JavaScript 문법 검사** - *.js 파일 syntax 검사 (node --check)
5. **필수 파일 존재 검사** - CLAUDE.md, PROGRESS.md, docs/ 7개 파일

### 하드코딩 탐지 기준
- IP 패턴: `[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}` (127.0.0.1, 0.0.0.0 제외)
- 비밀번호 패턴: `password *= *["']` (주석 제외)

## 수동 체크리스트

### 코드 품질
- [ ] JavaScript/JSON 코딩 스탠다드 준수
- [ ] 모든 함수에 JSDoc 작성
- [ ] 에러 처리 (try-catch) 포함
- [ ] 하드코딩 없음
- [ ] 단일 책임 원칙 (한 함수 = 한 기능)
- [ ] 의미 있는 변수명/함수명
- [ ] 복잡한 로직에 주석으로 이유 설명

### 워크플로우 품질
- [ ] JSON 문법 유효
- [ ] 노드 연결 정상
- [ ] 에러 핸들링 노드 포함
- [ ] 인증 정보 하드코딩 없음
- [ ] visual_type, meme_mood 등 필수 필드 포함

### 배포 전 확인
- [ ] quality-check.sh 통과
- [ ] git commit 완료
- [ ] n8n API 업로드 성공
- [ ] n8n 에디터 F5 새로고침
- [ ] 수동 실행 테스트 통과
- [ ] PROGRESS.md 업데이트

## 훅 설정 위치
`~/.claude/settings.json`에 PostToolUse 훅으로 설정
- Bash 도구 사용 후 자동 실행
- pwd로 프로젝트 디렉토리 확인 후 실행
