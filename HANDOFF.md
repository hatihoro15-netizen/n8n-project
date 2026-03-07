# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.

---

## A) 상태 요약
- **워크스페이스**: ~/n8n-worktrees/web (feature/web-app)
- **브랜치**: feature/web-app
- **Current Status**: Phase 2 완료 — 입력 필드 정리 + payload 계약 맞추기
- **Goal**: VPS 배포 + E2E 테스트

## B) 환경/의존성
- **서버**: VPS 76.13.182.180
- **환경**: Local + Prod
- **Required Secrets**: packages/backend/.env (VPS: /root/n8n-web/packages/backend/.env)
- **VPS_HOST**: 76.13.182.180 (.env에 추가됨)
- **PM2 프로세스명**: n8n-web-backend
- **CF Pages URL**: https://n8n-project-9lj.pages.dev
- **Backend URL**: https://api-n8n.xn--9g4bn4fm2bl2mb9f.com
- **n8n ao-produce workflow ID**: XV5shW265ht59MTD
- **n8n AO Worker workflow ID**: FHYohZccExR24Uha
- **n8n ao-generate-image workflow ID**: d5b35fb7f1724e448

## C) 마지막 실행 기록
- **Last Run Command**: TypeScript check + quality-check.sh
- **Result**: PASS
- **실행 위치**: Local
- **Last Commit**: (pending)

## D) 완료/미완료

### Done
- [x] Phase 2: 입력 필드 정리 + payload 계약 맞추기
  - prompt_p1 필수 (UI `*` 표시 + 백엔드 400 검증)
  - duration 드롭다운 (30/60/90/120초, 기본 30)
  - engine_type 선택 (5개: character_story/core_message/live_promo/meme/action_sports)
  - strict_mode 체크박스 (기본 false)
  - narration 3분리: narration_text(텍스트) + narration_style(스타일) + narration_tone(톤)
  - narration_mode 제거 (auto/manual → 비워두면 AI 자동)
  - BGM/SFX: 체크박스 → 파일 업로드 방식 (업로드 없으면 무음)
  - SFX 업로드 칸 신규 추가 (sfx_url)
  - topic/keywords/category: 접기 가능한 메타데이터 섹션으로 이동
  - n8n Producer 입력값 검증: topic/keywords/category 필수→선택, 새 필드 추가
  - sessionStorage draft 저장/복원 업데이트

### Next Actions
1. [ ] VPS 배포 (git pull + tsc + pm2 restart)
2. [ ] n8n Producer 워크플로우 업로드 (ao_producer.json → n8n API PUT)
3. [ ] E2E 영상 제작 테스트

## E) Blockers / Issues
- **Blockers**: kie.ai 크레딧 부족 (402) → 충전 필요
- **Known Issues**: n8n Worker가 새 필드(duration/engine_type/strict_mode/narration_style/narration_tone/sfx_url) 사용하려면 Worker 업데이트 필요

## F) 변경 파일
- productions-client.tsx (Phase 2 UI: duration/engine_type/strict_mode/narration 3분리/BGM·SFX 업로드/메타데이터 접기)
- productions.ts (body 타입 + prompt_p1·duration 검증 + webhook payload 신규 필드)
- ao_producer.json (입력값 검증 Code 노드: topic/keywords/category 선택, 신규 필드 추가)

## G) 다음 세션 시작용 메시지 (복붙용)
> Phase 2 완료: 입력 필드 정리 + payload 계약 맞추기. TypeScript + quality-check PASS. VPS 배포 + n8n 워크플로우 업로드 + E2E 테스트 필요.
