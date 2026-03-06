# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.

---

## A) 상태 요약
- **워크스페이스**: ~/n8n-worktrees/web (feature/web-app)
- **브랜치**: feature/web-app
- **Current Status**: 이미지 생성 버그 수정 + 내 사진으로 만들기 + n8n 웹훅 연결 완료 + VPS 배포
- **Goal**: E2E 실제 브라우저 테스트

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
  VPS: git pull + tsc + pm2 restart n8n-web-backend
  ```
- **Result**: PASS - PM2 online + ao-generate-image 웹훅 200 + 이미지 반환 확인
- **실행 위치**: VPS (SSH)
- **Last Commit**: `3ff04ce feat: 이미지 생성 버그 수정 + 내 사진으로 만들기 추가`

## D) 완료/미완료

### Done
- [x] 버그1: 프롬프트만으로 이미지 생성 버튼 활성화 (activeSlots 조건 제거)
- [x] 버그2: generate-image → n8n ao-generate-image 웹훅 경로 전환
- [x] 내 사진으로 만들기 섹션 (접기/펴기, 최대 10장, Claude Vision, 3가지 모드)
- [x] triggerWebhook 에러 핸들링 개선 (res.ok 체크)
- [x] ao-generate-image 웹훅 200 + 이미지 반환 E2E 확인
- [x] VPS 배포 + PM2 재시작

### Next Actions
1. [ ] 브라우저에서 이미지 생성 E2E 테스트 (프롬프트만 / 참조이미지+프롬프트 / 내사진+프롬프트)
2. [ ] ao-produce 웹훅 500 해결 (n8n 워크플로우 내부 문제)
3. [ ] 프론트엔드 브라우저 실제 동작 확인 (로그인 → 제작 → 이미지 생성 전체 플로우)

## E) Blockers / Issues
- **Blockers**: ao-produce 웹훅 500 (n8n 워크플로우 내부 실행 실패 — 웹훅 연결 자체는 정상)
- **Known Issues**: 없음

## F) 변경 파일
- packages/frontend/src/app/(dashboard)/images/images-client.tsx (버그 수정 + 내 사진 섹션)
- packages/backend/src/routes/media.ts (kie.ai → n8n webhook 전환)
- packages/backend/src/utils/n8n-client.ts (에러 핸들링)

## G) 다음 세션 시작용 메시지 (복붙용)
> 이미지 생성 버그 수정 + 내 사진 + n8n 웹훅 연결 완료. ao-generate-image 200 확인. ao-produce 500 (n8n 내부). 브라우저 E2E 테스트 필요.
