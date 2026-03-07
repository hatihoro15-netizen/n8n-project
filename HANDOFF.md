# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.

---

## A) 상태 요약
- **워크스페이스**: ~/n8n-worktrees/web (feature/web-app)
- **브랜치**: feature/web-app
- **Current Status**: Phase 2 완료 + 미디어 옵션 정리 + ao_producer.json 삭제 (아럽토 단일 관리)
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
- **Last Run Command**: git rm + commit
- **Result**: PASS
- **실행 위치**: Local
- **Last Commit**: a583931 chore: remove ao_producer.json from web workspace

## D) 완료/미완료

### Done
- [x] Phase 2: 입력 필드 정리 + payload 계약 맞추기
- [x] narration_style/narration_tone 한글 통일 (설명형/차분하게)
- [x] VPS 배포 + PM2 restart
- [x] 미디어 선택 옵션 정리 (generate 제거, analysis_only 고도화)
- [x] ao_producer.json 삭제 (아럽토 워크스페이스 단일 관리)

### Next Actions
1. [ ] 미커밋 변경 커밋 + VPS 배포
2. [ ] E2E 영상 제작 테스트
3. [ ] n8n Worker 새 필드 활용 (아럽토 워크스페이스 담당)

## E) Blockers / Issues
- **Blockers**: kie.ai 크레딧 부족 (402) → 충전 필요
- **Known Issues**: n8n Worker 새 필드(duration/engine_type/strict_mode 등) 활용은 아럽토 워크스페이스 담당
- **규칙**: n8n Producer/Worker 파일은 이 워크스페이스에서 수정하지 않음 (아럽토 단일 관리)

## F) 변경 파일
- productions-client.tsx (Phase 2 UI + generate 제거 + analysis_only 개선)
- productions.ts (body 타입 + 검증 + webhook payload)
- n8n-workflows/ 삭제 (아럽토 단일 관리)

## G) 다음 세션 시작용 메시지 (복붙용)
> Phase 2 + 미디어 옵션 정리 완료. ao_producer.json 삭제 (아럽토 단일 관리). 미커밋 변경 커밋 + VPS 배포 필요.
