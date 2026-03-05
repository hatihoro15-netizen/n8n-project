# CLAUDE.md — 운영 지침 (AO Pipeline)
> ⚠️ 최상위 규칙. 수정 시 이유/영향 먼저 보고.

## 프로젝트
- AO 프롬프트 기반 AI 영상 자동 제작 + 유튜브 업로드
- 워크스페이스: ~/n8n-worktrees/arubto-prompt
- 브랜치: feature/arubto-prompt
- VPS: root@76.13.182.180
- n8n: https://n8n.srv1345711.hstgr.cloud

## 기술 스택
| 레이어 | 기술 |
|--------|------|
| 프론트 | Next.js + Tailwind + shadcn/ui |
| DB/스토리지/인증 | Supabase (PostgreSQL + Storage + Auth) |
| 워크플로우 | n8n (셀프호스팅) |
| 이미지 생성 | Replicate API (Flux Pro/SDXL/Ideogram) |
| 텍스트 AI | Claude API / GPT-4o |
| TTS | ElevenLabs API |
| 영상 렌더링 | Creatomate API |
| 업로드 | YouTube API (OAuth 2.0) |

## 절대 규칙
1. **P1 원문 100% 보존** — 변경/요약/의역/삭제 절대 금지
2. **이미지 슬롯 자동 삽입** — images[1..4] → {IMG_1}~{IMG_4}
3. **프롬프트가 영상 결정** — 이미지 넣어도 프롬프트 지시가 우선
4. **구글 시트 금지** — 상태/로그 전부 Supabase DB
5. **한글 기본 지원** — 한글 입력 → 영문 번역 자동 생성
6. **자동 재시도** — AI API 실패 시 3회 자동 재시도

## 파일 역할
| 파일 | 역할 | 규칙 |
|---|---|---|
| CLAUDE.md | 운영 지침 | 고정 |
| HANDOFF.md | 세션 스냅샷 | 항상 전체 Overwrite |
| PROGRESS.md | 진행 일지 | 상단 요약만 Overwrite / 보고서 Append |
| docs/ | 정식 참조 문서 | 수정 시 보고 |

## 아키텍처: Producer / Worker / Queue
- Producer: 입력 수신 → 필수값 검사 → Job 생성 → Queue Push → job_id 반환
- Worker: Queue Pop → AO 조립 → 이미지 생성 → TTS → Creatomate 렌더 → 썸네일 → YouTube 업로드
- Job 상태: queued → processing → generated → uploading → uploaded / failed (3회 재시도)

## 작업 방식
최소변경 / 비밀값 출력·커밋 금지 / 계획 먼저 보고 후 작업 / 막히면 추측 금지

## 절대 금지
- 하드코딩 / 임시방편 / P1 원문 변경 / 구글 시트 사용
- 다른 워크트리(스포츠 픽 등) 파일 수정 금지
