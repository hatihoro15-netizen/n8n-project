# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.

---

## A) 상태 요약
- **워크스페이스**: ~/n8n-worktrees/web (feature/web-app)
- **브랜치**: feature/web-app
- **Current Status**: CF Pages 배포 정상 확인 (모든 페이지 200) + VPS 배포 완료
- **Goal**: n8n ao-produce 웹훅 E2E 테스트

## B) 환경/의존성
- **서버**: VPS 76.13.182.180
- **환경**: Local + Prod
- **Required Secrets**: packages/backend/.env (VPS: /root/n8n-web/packages/backend/.env)
- **VPS_HOST**: 76.13.182.180 (.env에 추가됨)
- **PM2 프로세스명**: n8n-web-backend
- **CF Pages URL**: https://n8n-project-9lj.pages.dev
- **Backend URL**: https://api-n8n.xn--9g4bn4fm2bl2mb9f.com

## C) 마지막 실행 기록
- **Last Run Command**:
  ```
  curl -s -o /dev/null -w "%{http_code}" https://n8n-project-9lj.pages.dev/{,productions,images,login}
  ```
- **Result**: PASS - 모든 페이지 HTTP 200
- **실행 위치**: Local
- **Last Commit**: `49ffdf5 feat: Cloudflare Pages 빌드 + 작업 큐 실시간 상태 표시`

## D) 완료/미완료

### Done
- [x] Cloudflare Pages 프론트엔드 배포 정상 확인 (/, /productions, /images, /login 모두 200)
- [x] GET /api/productions/:id/status 경량 상태 조회 엔드포인트
- [x] 폴링 간격 10초 → 2초 (경량 API 사용)
- [x] JobProgressBar 컴포넌트 (상태별 퍼센트 바)
- [x] failed 시 재시도 버튼
- [x] VPS 배포 + PM2 재시작

### Next Actions
1. [ ] n8n ao-produce 웹훅 워크플로우 활성화 + E2E 테스트
2. [ ] 이미지 생성 E2E 테스트 (kie.ai API 키 필요)
3. [ ] 프론트엔드 브라우저 실제 동작 확인 (로그인 → 제작 → 이미지 생성)

## E) Blockers / Issues
- **Blockers**: n8n ao-produce 웹훅 워크플로우 활성화 필요
- **Known Issues**: 없음

## F) 변경 파일
- 이번 세션: 코드 변경 없음 (CF Pages 배포 확인만)

## G) 다음 세션 시작용 메시지 (복붙용)
> CF Pages 배포 정상 (모든 페이지 200) + VPS 배포 완료. n8n 웹훅 E2E 테스트 필요.
