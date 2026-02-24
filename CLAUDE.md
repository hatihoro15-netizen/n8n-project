# n8n 워크플로우 프로젝트 - 작업 규칙

## 작업 시작 전 체크리스트
- [ ] 작업 유형 확인 → 관련 docs 파일만 읽기
- [ ] PROGRESS.md 읽기
- [ ] git status 확인
- [ ] 수정할 파일 역할 확인 (docs/03-file-roles.md)
- [ ] 수정 전 git commit

## 작업 완료 후 체크리스트
- [ ] quality-check.sh 실행 및 통과
- [ ] 기능 실제 동작 확인
- [ ] git commit
- [ ] PROGRESS.md 업데이트 (보고서 형식)

## 절대 규칙
- IP 하드코딩 금지 (모든 IP는 설정 파일 또는 환경변수에서 읽기)
- 임시방편 조치 금지
- 근본 원인 파악 없이 재시도 금지
- 파일 전체 교체 금지 (필요한 부분만 수정)
- 동작 중인 기능 건드리기 금지
- 여러 파일 동시 수정 금지
- 커밋 없이 수정 시작 금지
- 확실하지 않으면 작업 중단하고 질문

## 코드 품질 기준
- JavaScript/JSON 코딩 스탠다드 준수
- 모든 함수에 JSDoc 작성
- 에러 처리 필수 (try-catch)
- 하드코딩 금지, 단일 책임 원칙
- 의미 있는 변수명/함수명 사용
- 복잡한 로직은 주석으로 이유 설명

## 작업 유형별 읽을 파일
| 작업 유형 | 읽을 파일 |
|-----------|-----------|
| 구조/설계 | docs/01-architecture.md |
| 서버/인프라 | docs/02-infra-rules.md |
| 파일 수정 | docs/03-file-roles.md |
| 기능 개발 | docs/04-workflow.md |
| 품질 검사 | docs/05-quality-check.md |
| 에러 대응 | docs/06-error-patterns.md |
| 보고서 | docs/07-report-template.md |
