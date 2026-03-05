# CLAUDE.md — 운영 지침 (AO Pipeline)
> ⚠️ 최상위 규칙. 수정 시 이유/영향 먼저 보고.

## 프로젝트
- AO 프롬프트 기반 영상 자동화 파이프라인
- 워크스페이스: ~/n8n-worktrees/arubto-prompt
- 브랜치: feature/arubto-prompt
- VPS: root@76.13.182.180
- n8n: https://n8n.srv1345711.hstgr.cloud

## 절대 규칙
1. **P1 원문 100% 보존** — 변경/요약/의역/삭제 절대 금지
2. **이미지 슬롯 자동 삽입** — images[1..4] → {IMG_1}~{IMG_4}
3. **프롬프트가 영상 결정** — 이미지 넣어도 프롬프트 지시가 우선
4. **구글 시트 금지** — 상태/로그 전부 Postgres DB
5. **한글 기본 지원** — 한글 입력 → 영문 번역 자동 생성

## 파일 역할
| 파일 | 역할 | 규칙 |
|---|---|---|
| CLAUDE.md | 운영 지침 | 고정 |
| HANDOFF.md | 세션 스냅샷 | 항상 전체 Overwrite |
| PROGRESS.md | 진행 일지 | 상단 요약만 Overwrite / 보고서 Append |
| docs/ | 정식 참조 문서 | 수정 시 보고 |

## 아키텍처: Producer / Worker / Queue
- Producer: 입력 수신 → 필수값 검사 → Job 생성 → Queue Push → job_id 반환
- Worker: Queue Pop → AO 조립 → 씨덴스 실행 → 결과 저장 → 업로드 → 상태 업데이트
- Job 상태: queued → processing → generated → uploading → uploaded / failed

## 작업 방식
최소변경 / 비밀값 출력·커밋 금지 / 계획 먼저 보고 후 작업 / 막히면 추측 금지

## 절대 금지
- 하드코딩 / 임시방편 / P1 원문 변경 / 구글 시트 사용
- 다른 워크트리(스포츠 픽 등) 파일 수정 금지
