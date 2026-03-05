# process.md — 재사용 지식 베이스 (프로젝트 전용)

> ❌ 이 파일은 프로젝트 지식베이스입니다. Overwrite/삭제 금지(append만). 정리(압축)가 필요해도 ADR/트러블슈팅 핵심은 남기고, 중복만 줄입니다.

🔎 INDEX: 적용 우선순위 | 기본 환경 | 기술 스택 | 폴더/파일 표준 | 필수 원칙 | 롤백 | ADR | 트러블슈팅(Symptom/Steps/Cause/Fix/Prevention)

---

## 0) 적용 우선순위
- 이 문서(process.md)의 규칙이 일반적인 관습/LLM 기본 스타일보다 우선한다.

## 1) 프로젝트 기본 환경 (고정)
- 프로젝트: N8 Video Manager (AI 기반 유튜브 숏폼 자동 제작 플랫폼)
- VPS: 76.13.182.180 (Hostinger KVM1)
- n8n URL: https://n8n.srv1345711.hstgr.cloud
- 프론트: https://n8n-project-9lj.pages.dev (Cloudflare Pages)
- 백엔드 API: https://api-n8n.xn--9g4bn4fm2bl2mb9f.com
- 운영 워크스페이스: 웹앱 / n8n 온카 / n8n 흑형·할머니·스포츠 / n8n 루믹스 / n8n 스포츠(아럽토)

## 1-1) 기술 스택
- 언어/런타임: TypeScript / Node.js
- 프론트: Next.js (Cloudflare Pages)
- 백엔드: Fastify + Prisma
- DB: PostgreSQL (VPS 내부)
- 자동화: n8n (self-hosted, Docker)
- TTS: edge-tts (Docker)
- 영상 합성: NCA FFmpeg (Docker)
- AI 스크립트: Gemini
- 스토리지: MinIO (Docker, http://76.13.182.180:9000)
- 배포: Cloudflare Pages(프론트) + PM2(백엔드 VPS)
- 프로세스 매니저: PM2

## 1-2) 폴더/파일 구조 표준 (모노레포)
```
n8n-project/
├── packages/
│   ├── frontend/     (Next.js)
│   ├── backend/      (Fastify + Prisma)
│   └── shared/       (공유 타입)
├── deploy/
│   └── ecosystem.config.js  (PM2 설정)
└── ...
```
- VPS 서버 경로: `/root/n8n-web/`
- 백엔드 환경변수: `/root/n8n-web/packages/backend/.env`
- n8n 워크플로우 백업: Export JSON으로 관리
- 설정 파일: 환경변수(.env)로 관리, 절대 하드코딩 금지

## 2) 필수 작업 원칙 (강제 규칙)
- **VPS 서버 작업 전 반드시 현재 상태 백업 확인**
- **n8n 워크플로우 수정 전 반드시 Export(JSON) 백업**
- 작업 시작 전 반드시 대상 워크스페이스 명시
- API 호출 최소화 (Gemini, edge-tts 등 유료 API 비용 절감)
- 롤백 방법 확인 후 변경 작업 진행

## 3) n8n 필수 주의사항
- **top-level nodes와 activeVersion.nodes 양쪽 다 수정** (한쪽만 수정하면 구버전 실행됨)
- **직렬 노드 삽입 시 이후 노드의 $json 참조 확인** — `$('원본노드명').first().json.xxx`로 명시적 참조
- **Google Sheets update 노드는 alwaysOutputData: true 필수** (매칭 행 없으면 이후 노드 미실행)
- **HTTP Request JSON body**: specifyBody:"json" 모드에서 JSON.stringify() 쓰면 이중 직렬화 주의

## 4) 롤백 가이드
- n8n 워크플로우: 백업 JSON Import로 복원
- VPS 설정: 변경 전 파일 `.bak` 복사본 유지
- 컨테이너: `docker-compose down && docker-compose up -d`
- 백엔드: PM2 `pm2 restart ecosystem.config.js`

## 5) 결정 기록 (ADR — 짧게)

### ADR 형식
- 결론:
- 이유:
- 대안/배제:
- 영향:

## 6) 프로젝트 전용 트러블슈팅 (오염 방지)
- 중요 에러 해결 시 반드시 아래 템플릿으로 기록
- 기록 대상: 이 프로젝트에서만 의미 있는 설정/버전 충돌/재현 어려운 버그
- 기록 금지: 기초 문법/단순 오타/일회성 에러

### 트러블슈팅 형식
```
### [YYYY-MM-DD] (증상 한 줄)
- 상황(Context):
- 재현(Steps):
- 원인(Cause):
- 해결(Fix):
- 검증(Command/Result):
- 예방(Prevention):
- 관련 파일:
```

---

## 기존 누적 지식 (Append)

### 기존 환경 참고 (n8n 워크플로우 관련)
- n8n 설치 경로: /home/user/n8n (컨테이너 queue-mode)
- MinIO: VPS 내 자체 호스팅
- 영상 생성: Kie.ai (Veo3 Fast, Kling), fal.ai
- TTS (레거시): ElevenLabs
- 영상 합성 (레거시): NCA Toolkit + FFmpeg
- n8n 워크플로우 백업 경로: `/home/user/n8n/backups/`
- 영상 출력: MinIO 버킷 기준 관리
- FFmpeg 필터 한국어 텍스트 처리 시 폰트 경로 명시 필수
