# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.

---

## A) 상태 요약
- **워크스페이스**: ~/n8n-worktrees/web (feature/web-app)
- **브랜치**: feature/web-app
- **Current Status**: 씬 duration 검증 1~12s Kling 제약 통일 완료
- **Goal**: E2E 영상 제작 테스트

## B) 환경/의존성
- **서버**: VPS 76.13.182.180
- **환경**: Local + Prod
- **Required Secrets**: packages/backend/.env (VPS: /root/n8n-web/packages/backend/.env)
- **PM2 프로세스명**: n8n-web-backend
- **CF Pages URL**: https://n8n-project-9lj.pages.dev
- **CF Pages 프로젝트명**: n8n-project
- **CF Pages Production Branch**: feature/web-app (--branch=feature/web-app 필수!)
- **Backend URL**: https://api-n8n.xn--9g4bn4fm2bl2mb9f.com

## C) 마지막 실행 기록
- **Last Run Command**: npx next build (frontend)
- **Result**: PASS
- **실행 위치**: Local
- **Last Commit**: fix(web): align scene duration validation to 1~12s kling constraint

## D) 완료/미완료

### Done
- [x] F-3~F-6 UI 기능 전체 완료
- [x] 2단계 그룹/샷 플래너 UI + voice_provider + payload preview
- [x] processing callback updatedAt 갱신 (no-op 해제)
- [x] PRODUCTION_TIMEOUT_MINUTES 기본값 5 → 20분
- [x] 씬 duration 검증 1~12s 통일 + payload preview 범위 경고

### Next Actions
1. [ ] CF Pages 배포
2. [ ] E2E 영상 제작 테스트
3. [ ] main 머지

## E) Blockers / Issues
- **규칙**: slideshow 모드 코드 수정 금지
- **규칙**: n8n Producer/Worker 파일은 이 워크스페이스에서 수정하지 않음

## F) 변경 파일
- packages/frontend/src/app/(dashboard)/productions/productions-client.tsx (duration max=12, 경고 >12, payload preview 범위 체크)

## G) 다음 세션 시작용 메시지 (복붙용)
> 씬 duration 검증 1~12s Kling 제약 통일 완료. CF Pages 배포 후 E2E 테스트 필요.
