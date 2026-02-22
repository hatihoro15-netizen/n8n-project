# 05. 품질 검사 규칙

## 자동 검사 (quality-check.sh)
스크립트 위치: `scripts/quality-check.sh`
실행: Bash 도구 사용 후 자동 실행 (PostToolUse 훅)

### 검사 항목 (5단계)
1. **JSON 문법 검사** - 모든 .json 파일 유효성 검증
2. **Python 문법 검사** - py 파일 syntax 검사
3. **하드코딩 검사** - IP 주소, 비밀번호 등 하드코딩 탐지 (py/js 대상)
4. **JavaScript 문법 검사** - n8n Code 노드용 .js 파일 syntax 검사
5. **필수 파일 존재 검사** - 프로젝트 필수 파일 존재 여부

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
- [ ] 웹훅 URL 정상
- [ ] 인증 정보 하드코딩 없음

### 배포 전 확인
- [ ] 로컬 테스트 통과
- [ ] quality-check.sh 통과
- [ ] git commit 완료
- [ ] PROGRESS.md 업데이트
