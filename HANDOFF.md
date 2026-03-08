# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.

---

## A) 상태 요약
- **워크스페이스**: ~/n8n-worktrees/web (feature/web-app)
- **브랜치**: feature/web-app
- **Current Status**: Kling 그룹핑 모드 선택 UI 추가 완료
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
- **Result**: PASS — 빌드 성공
- **실행 위치**: Local
- **Last Commit**: feat(ui): add kling grouping mode selector with manual group targets

## D) 완료/미완료

### Done
- [x] F-3~F-6 UI 기능 전체 완료
- [x] Production params 영속화 (assets.params) + 상세 UI 노출
- [x] F-6 AI 추천 → scenes 배열 + 멀티클립 UI
- [x] 상세 페이지: 제작 중 → 스피너만, 완료/실패/정지 → 제작 정보 표시
- [x] 멀티클립 씬 0개 시 빈 상태 UI 유지
- [x] 영상 길이: 드롭다운 → 슬라이더+직접입력 (0~180초)
- [x] 나레이션 타이밍 선택 UI (AI 자동 배치 / 직접 지정)
- [x] Kling 샷 제약 안내 (multi_shots 모드 전환 안내)
- [x] 샷 duration 경고 기준 13초 통일, non-blocking, 상한 clamp 제거
- [x] Kling 그룹핑 모드 선택 (auto_pack/manual) + 수동 그룹 목표 시간 UI

### Next Actions
1. [ ] CF Pages 배포
2. [ ] E2E 영상 제작 테스트
3. [ ] main 머지

## E) Blockers / Issues
- **Blockers**: n8n Producer duration 화이트리스트 (arubto-prompt에서 수정 필요)
- **규칙**: slideshow 모드 코드 수정 금지
- **규칙**: n8n Producer/Worker 파일은 이 워크스페이스에서 수정하지 않음
- **CF Pages 배포**: `--branch=feature/web-app` 필수 + `.next`/`.vercel` 캐시 삭제 후 빌드

## F) 변경 파일
- packages/frontend/src/app/(dashboard)/productions/productions-client.tsx (그룹핑 모드 선택 UI)

## G) 다음 세션 시작용 메시지 (복붙용)
> Kling 그룹핑 모드 선택 UI 완료. auto_pack/manual 라디오 + 수동 그룹 목표 시간 입력. CF Pages 배포 + E2E 테스트 필요.
