# CLAUDE.md — 운영 지침 (AO Pipeline)
> ⚠️ 최상위 규칙. 수정 시 이유/영향 먼저 보고.

## 파일 역할
| 파일 | 역할 | 규칙 |
|---|---|---|
| CLAUDE.md | 운영 지침 | 고정 |
| HANDOFF.md | 세션 스냅샷 | 항상 전체 Overwrite |
| PROGRESS.md | 진행 일지 | 상단 요약만 Overwrite / 보고서 Append |
| docs/ | 정식 참조 문서 | 수정 시 보고 |
> Next/LastRun/Blockers 정답 = HANDOFF.md (예외 없음)

## 우선순위: 사용자 지시 > CLAUDE > HANDOFF > PROGRESS/docs

## 프로젝트
- AO 프롬프트 기반 AI 영상 자동 제작 + 유튜브 업로드
- N8 Video Manager / VPS: 76.13.182.180 / n8n: https://n8n.srv1345711.hstgr.cloud
- 워크스페이스: ~/n8n-worktrees/arubto-prompt / 브랜치: feature/arubto-prompt
> ⚠️ 워크스페이스 확정 전 코드/서버 변경 금지

## 기술 스택
| 레이어 | 기술 |
|--------|------|
| 프론트 | Next.js + Tailwind + shadcn/ui |
| DB/스토리지/인증 | Supabase (PostgreSQL + Storage + Auth) |
| 워크플로우 | n8n (셀프호스팅) |
| 영상 생성 | kie.ai Seedance API |
| 텍스트 AI | Claude API |
| TTS | kie.ai (ElevenLabs 모델) |
| 영상 렌더링 | Creatomate API |
| 업로드 | YouTube API (OAuth 2.0) |

## 세션 시작 루틴 (INIT)
순서: HANDOFF → PROGRESS(요약+최근1개) → 해당 docs만
docs 목차: 01 아키텍처 / 02 인프라 / 03 파일역할 / 04 워크플로우 / 05 품질 / 06 에러 / 07 보고서

첫 응답 브리핑(필수):
📝 현재 상태 / 🎯 목표 / ➡️ Next Top3(HANDOFF) / ⚠️ Blockers / 📌 주의규칙 Top3
> ⚠️ 브리핑 + 계획 출력 전 작업 시작 금지

## 절대 규칙
1. **P1 원문 100% 보존** — 변경/요약/의역/삭제 절대 금지
2. **이미지 슬롯 자동 삽입** — images[1..4] → {IMG_1}~{IMG_4}
3. **프롬프트가 영상 결정** — 이미지 넣어도 프롬프트 지시가 우선
4. **구글 시트 금지** — 상태/로그 전부 Supabase DB
5. **한글 기본 지원** — 한글 입력 → 영문 번역 자동 생성
6. **자동 재시도** — AI API 실패 시 3회 자동 재시도

## 아키텍처: Producer / Worker / Queue
- Producer: 입력 수신 → 필수값 검사 → Job 생성 → Queue Push → job_id 반환
- Worker: Queue Pop → AO 조립 → Seedance 영상 → TTS → Creatomate 렌더 → YouTube 업로드
- Job 상태: queued → processing → generated → uploading → uploaded / failed (3회 재시도)

## 작업 방식
최소변경 / 비밀값 출력·커밋 금지 / 계획 먼저 보고 후 작업 / 막히면 추측 금지

## 완료 체크
- [ ] quality-check.sh PASS / 동작 확인 / git commit
- [ ] HANDOFF Overwrite / PROGRESS 요약 갱신 + 보고서 Append
말미: ✅한일 / 📁파일 / 🧪테스트 / ⚠️이슈 / ➡️다음

## 절대 금지
- 하드코딩 / 임시방편 / P1 원문 변경 / 구글 시트 사용
- 다른 워크트리(스포츠 픽 등) 파일 수정 금지
- n8n: API업로드 후 F5필수 / top-level+activeVersion양쪽수정 / $json체인확인 / alwaysOutputData
- 중단조건: 동작중기능수정 / 파일삭제 / 방법불확실 / 요구사항모호 / 예상외에러
