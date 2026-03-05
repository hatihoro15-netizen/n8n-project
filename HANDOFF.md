# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.

---

## A) 상태 요약
- **워크스페이스**: ~/n8n-worktrees/web (feature/web-app)
- **브랜치**: feature/web-app
- **Current Status**: 숏폼/롱폼 선택 UI 추가 완료 + VPS 배포 완료
- **Goal**: n8n ao-produce 웹훅 E2E 테스트

## B) 환경/의존성
- **서버**: VPS 76.13.182.180
- **환경**: Local + Prod
- **Required Secrets**: packages/backend/.env (VPS: /root/n8n-web/packages/backend/.env)
- **VPS_HOST**: 76.13.182.180 (.env에 추가됨)
- **PM2 프로세스명**: n8n-web-backend

## C) 마지막 실행 기록
- **Last Run Command**:
  ```
  VPS: git pull + npm install + tsc + pm2 restart n8n-web-backend
  ```
- **Result**: PASS - PM2 online, tsc 통과
- **실행 위치**: VPS (SSH)
- **Last Commit**: `a79b484 feat: 숏폼/롱폼 선택 UI 추가`

## D) 완료/미완료

### Done
- [x] 숏폼/롱폼 선택 UI (워크플로우 아래, 제작 방식 위)
- [x] aspect_ratio 웹훅 payload 추가 (프론트+백엔드)
- [x] VPS 배포 + PM2 재시작

### Next Actions
1. [ ] n8n ao-produce 웹훅 워크플로우 활성화 + E2E 테스트
2. [ ] 영상 제작 완료 후 미리보기 확인
3. [ ] Cloudflare Pages 프론트엔드 빌드 확인

## E) Blockers / Issues
- **Blockers**: n8n ao-produce 웹훅 워크플로우 활성화 필요
- **Known Issues**: 없음

## F) 변경 파일
- productions-client.tsx (aspectRatio 상태 + 숏폼/롱폼 버튼 UI + payload)
- productions.ts (aspect_ratio body 타입 + 웹훅 전달)

## G) 다음 세션 시작용 메시지 (복붙용)
> 숏폼/롱폼 선택 UI + VPS 배포 완료. n8n ao-produce 웹훅 E2E 테스트 필요.
