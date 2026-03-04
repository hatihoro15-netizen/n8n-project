# process.md — 재사용 지식 베이스 (프로젝트 전용)

## 0) 적용 우선순위
- 이 문서(process.md)의 규칙이 일반적인 관습/LLM 기본 스타일보다 우선한다.

## 1) 프로젝트 기본 환경 (고정)
- VPS: 76.13.182.180 (Hostinger KVM1, Malaysia)
- n8n URL: https://n8n.srv1345711.hstgr.cloud
- n8n 설치 경로: /home/user/n8n (컨테이너 queue-mode)
- MinIO: VPS 내 자체 호스팅
- 운영 프로젝트: 온카스터디 / LUMIX SOLUTION / BankNotifyTelegram / 스트리밍팀(Zoo·Guardian·Life)

## 1-1) 기술 스택
- 언어/런타임: Python 3.11 (백엔드), Node.js (n8n 워크플로우)
- 자동화: n8n (self-hosted, queue-mode)
- 영상 생성: Kie.ai (Veo3 Fast, Kling), fal.ai
- TTS: ElevenLabs
- AI 스크립트: Gemini
- 영상 합성: NCA Toolkit + FFmpeg
- 스토리지: MinIO
- 배포: YouTube API

## 1-2) 폴더/파일 구조 표준
- n8n 워크플로우 백업: `/home/user/n8n/backups/`
- 영상 출력: MinIO 버킷 기준 관리
- 설정 파일: 환경변수(.env)로 관리, 절대 하드코딩 금지

## 2) 필수 작업 원칙 (강제 규칙)
- **VPS 서버 작업 전 반드시 현재 상태 백업 확인**
- **n8n 워크플로우 수정 전 반드시 Export(JSON) 백업**
- 여러 프로젝트 동시 운영 중 — 작업 시작 전 반드시 대상 프로젝트 명시
- API 호출 최소화 (Kie.ai, ElevenLabs, Gemini 등 유료 API 비용 절감)
- FFmpeg 필터 한국어 텍스트 처리 시 폰트 경로 명시 필수
- 롤백 방법 확인 후 변경 작업 진행

## 3) 롤백 가이드
- n8n 워크플로우: 백업 JSON Import로 복원
- VPS 설정: 변경 전 파일 `.bak` 복사본 유지
- 컨테이너: `docker-compose down && docker-compose up -d`

## 4) 결정 기록 (ADR — 짧게)

### ADR-형식
- 결론:
- 이유:
- 대안/배제:
- 영향:

## 5) 프로젝트 전용 트러블슈팅 (오염 방지)
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
