# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.

---

## A) 상태 요약
- **워크스페이스**: ~/n8n-worktrees/web (feature/web-app)
- **브랜치**: feature/web-app
- **Current Status**: CF Pages + VPS 재배포 완료 (8a0a609). E2E 테스트 대기
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
- **n8n ao-produce workflow ID**: XV5shW265ht59MTD
- **n8n AO Worker workflow ID**: FHYohZccExR24Uha
- **n8n ao-generate-image workflow ID**: d5b35fb7f1724e448

## C) 마지막 실행 기록
- **Last Run Command**: CF Pages wrangler deploy --branch=feature/web-app + VPS ssh deploy
- **Result**: PASS — CF Pages 200 OK + VPS PM2 online + Backend API 200 OK
- **실행 위치**: Local → Remote
- **Last Commit**: 8a0a609 fix: allow production start without images

## D) 완료/미완료

### Done
- [x] Phase 2: 입력 필드 정리 + payload 계약 맞추기
- [x] 클립 길이 + 구 duration 완전 제거 (프론트+백엔드)
- [x] 영상 길이 드롭다운 1개로 통합 (자동(AI 판단)/10~60초)
- [x] CF Pages Production 브랜치 문제 수정
- [x] B-2: analysis_only Vision 자동 분석 미동작 수정
- [x] 이미지 없이 영상 제작 시작 허용
- [x] CF Pages + VPS 재배포 (8a0a609 반영)

### Next Actions
1. [ ] E2E 영상 제작 테스트 (kie.ai 크레딧 충전 완료)
2. [ ] main 머지
3. [ ] 프로덕션 안정화

## E) Blockers / Issues
- **Blockers**: 없음
- **규칙**: slideshow 모드 코드 수정 금지
- **규칙**: n8n Producer/Worker 파일은 이 워크스페이스에서 수정하지 않음
- **CF Pages 배포**: `--branch=feature/web-app` 필수 + `.next`/`.vercel` 캐시 삭제 후 빌드
- **payload**: duration_sec만 사용 (0=자동, 그 외 초 값)
- **상수**: NARRATION_CHARS_PER_SEC = 4

## F) 변경 파일
- 없음 (배포만 수행)

## G) 다음 세션 시작용 메시지 (복붙용)
> CF Pages + VPS 재배포 완료 (8a0a609). E2E 영상 제작 테스트 진행 필요.
