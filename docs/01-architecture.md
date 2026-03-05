# 01-architecture.md — 시스템 구조/서버 구성/데이터 흐름

## 시스템 구성
- n8n: 워크플로우 오케스트레이션 (self-hosted, Docker)
- TTS: edge-tts (Docker)
- 영상 합성: NCA FFmpeg (Docker)
- 스토리지: MinIO (http://76.13.182.180:9000)
- AI 스크립트: Gemini API
- 배포: Cloudflare Pages(프론트) + PM2(백엔드 VPS)

## 기술 스택
- 언어: TypeScript / Node.js
- 프론트: Next.js (Cloudflare Pages)
- 백엔드: Fastify + Prisma + PostgreSQL
- 자동화: n8n

## 데이터 흐름
1) 웹앱 트리거 → 2) n8n 웹훅 → 3) Gemini 스크립트 생성
→ 4) edge-tts TTS → 5) 이미지 수집 → 6) NCA 영상 합성
→ 7) MinIO 저장 → 8) 웹앱 콜백

## 서버/환경
- VPS: 76.13.182.180 (Hostinger KVM1)
- n8n: https://n8n.srv1345711.hstgr.cloud
- 프론트: https://n8n-project-9lj.pages.dev
- 백엔드: https://api-n8n.xn--9g4bn4fm2bl2mb9f.com

## 에이전트 팀 역할
| 역할 | 담당 |
|---|---|
| 인프라 에이전트 | 서버/배포/n8n 인스턴스/infra 파일 |
| 워크플로우 에이전트 | n8n 노드/연결/로직/*.json |
| 콘텐츠 에이전트 | 프롬프트/캐릭터/대사/콘텐츠 노드 |
| 검증 에이전트 | 테스트/lint/동작 확인 |

에이전트 규칙:
- 자기 역할 외 파일 수정 금지
- 작업 전 관련 docs/ 읽기
- 작업 완료 후 보고서 작성 (발견/수정/판단/파일/검증)
