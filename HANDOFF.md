# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.

---

## A) 상태 요약
- **워크스페이스**: ~/n8n-worktrees/web (feature/web-app)
- **브랜치**: feature/web-app
- **Current Status**: sfx_url 키 불일치 수정 + params snapshot 필드 추가 + timeout-checker 주석 수정 완료
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
- **Last Run Command**: npx tsc --noEmit (backend)
- **Result**: PASS
- **실행 위치**: Local
- **Last Commit**: fix(web): fix sfx url key mismatch and add missing params snapshot fields

## D) 완료/미완료

### Done
- [x] F-3~F-6 UI 기능 전체 완료
- [x] 2단계 그룹/샷 플래너 UI + voice_provider + payload preview
- [x] processing callback updatedAt 갱신 (no-op 해제)
- [x] PRODUCTION_TIMEOUT_MINUTES 기본값 5 → 20분
- [x] 씬 duration 검증 1~12s 통일 + payload preview 범위 경고
- [x] webhook payload에 voice_provider, kling_grouping_mode, kling_group_targets, kling_group_shots 추가
- [x] AI 추천 씬 자동 덮어쓰기 금지 (미리보기 + 적용 버튼 분리)
- [x] suggest-prompt 씬 길이 범위 3~15 → 1~12 수정
- [x] sfx_url → sfx_file_url 키 매핑 (Producer 호환)
- [x] params snapshot에 voice_provider, kling_grouping_mode, kling_group_targets, kling_group_shots 추가
- [x] timeout-checker 주석 5분 → 20분 수정

### Next Actions
1. [ ] VPS 백엔드 배포 (git pull + pm2 restart)
2. [ ] CF Pages 배포
3. [ ] E2E 영상 제작 테스트

## E) Blockers / Issues
- **규칙**: slideshow 모드 코드 수정 금지
- **규칙**: n8n Producer/Worker 파일은 이 워크스페이스에서 수정하지 않음
- **VPS 배포 필요**: 백엔드 코드 변경 반영하려면 VPS에서 git pull + pm2 restart 필요

## F) 변경 파일
- packages/backend/src/routes/productions.ts (sfx_url→sfx_file_url 매핑, params snapshot 4필드 추가)
- packages/backend/src/jobs/timeout-checker.ts (주석 5분→20분)

## G) 다음 세션 시작용 메시지 (복붙용)
> sfx_url 키 수정 + params snapshot 필드 추가 + timeout 주석 수정 완료. VPS + CF Pages 배포 후 E2E 테스트 필요.
