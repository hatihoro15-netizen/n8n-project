# 01. 시스템 아키텍처

## 서버 구성

### NCA 서버 (환경변수: NCA_HOST)
- Docker 기반 멀티 컨테이너 환경
- Traefik: 리버스 프록시 (포트 80/443)
- n8n: 워크플로우 자동화 엔진
- NCA Toolkit: FFmpeg API (포트 8080)
- MinIO: S3 호환 오브젝트 스토리지 (포트 9000/9001)
- PostgreSQL: 데이터베이스
- Redis: 캐시
- edge-tts API: TTS 엔진 (포트 5100)

### 외부 서비스
- n8n 웹 UI: https://n8n.srv1345711.hstgr.cloud
- Google Sheets: 주제 관리 및 결과 기록
- Pexels API: 이미지 검색
- Google Gemini API: AI 콘텐츠 생성
- Tenor CDN: 밈/리액션 GIF 소스

## 데이터 흐름
```
Google Sheet(주제)
  → n8n 워크플로우
  → AI(Gemini): 콘텐츠 생성
  → 콘텐츠 파싱
  → 병렬 처리:
      ├─ TTS(edge-tts): 음성 생성
      └─ 이미지(Pexels) / 밈(MinIO): 비주얼 소스
  → NCA Toolkit(FFmpeg): 영상 합성
  → 영상 URL
  → Google Sheet(결과 기록)
```

## 에이전트 역할 정의

### 인프라 에이전트
- **담당**: 서버, 배포, n8n 인스턴스 관리
- **접근 가능 파일**: 서버 설정, Docker 구성, 인프라 스크립트, setup_*.sh
- **금지**: 워크플로우 JSON, 콘텐츠 프롬프트 수정

### 워크플로우 에이전트
- **담당**: n8n 노드 구성, 노드 간 연결, 워크플로우 로직
- **접근 가능 파일**: *.json 워크플로우 파일, *.py 생성/업데이트 스크립트
- **금지**: 서버 설정, AI 프롬프트 내용 수정

### 콘텐츠 에이전트
- **담당**: AI 프롬프트, 캐릭터 설정, 대사 작성
- **접근 가능 파일**: 프롬프트 텍스트, 캐릭터 설정값, 콘텐츠 관련 노드 jsCode
- **금지**: 워크플로우 구조, 서버 인프라 수정

### 검증 에이전트
- **담당**: 테스트, lint, 동작 확인
- **접근 가능 파일**: scripts/, 테스트 파일, docs/
- **금지**: 프로덕션 코드 직접 수정

### 에이전트 공통 규칙
1. 자기 역할 외 파일 수정 절대 금지
2. 작업 전 반드시 관련 docs 파일 읽기
3. 작업 완료 후 반드시 보고서 작성:
   - 뭘 발견했는지
   - 뭘 수정했는지
   - 왜 그렇게 판단했는지
   - 수정된 파일 목록
   - 검증 결과

## 프로젝트 디렉토리 구조
```
n8n-project/
├── CLAUDE.md              # 작업 규칙 (50줄 이내)
├── PROGRESS.md            # 작업 기록 및 현재 상태
├── docs/                  # 매뉴얼 시스템 (7개 파일)
│   ├── 01-architecture.md # 시스템 구조, 서버, 에이전트
│   ├── 02-infra-rules.md  # 인프라/서버 규칙
│   ├── 03-file-roles.md   # 파일별 역할, 혼용 금지
│   ├── 04-workflow.md     # 작업 흐름, 의사결정, 롤백
│   ├── 05-quality-check.md# 품질 검사 규칙
│   ├── 06-error-patterns.md# 에러 패턴, 금지 패턴
│   └── 07-report-template.md# 보고서 양식
├── scripts/
│   └── quality-check.sh   # 품질 검사 스크립트 (자동 실행)
├── .claude/commands/
│   └── start.md           # /start 세션 시작 명령
├── *.json                 # n8n 워크플로우 파일
└── *.py                   # 워크플로우 생성/업데이트 스크립트
```
