# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.

---

## A) 상태 요약
- **워크스페이스**: ~/n8n-worktrees/web (feature/web-app)
- **브랜치**: feature/web-app
- **Current Status**: 이미지 생성 → 영상 제작 자동 연동 완료 + VPS 배포 완료
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
  VPS: git pull + tsc + pm2 restart n8n-web-backend
  ```
- **Result**: PASS - PM2 online
- **실행 위치**: VPS (SSH)
- **Last Commit**: `e9c8743 feat: 이미지 생성 → 영상 제작 자동 연동`

## D) 완료/미완료

### Done
- [x] 이미지 생성 → 영상 제작 자동 연동
- [x] localStorage `pending_production_images` 키로 이미지 URL 전달
- [x] WhiskProductionForm 마운트 시 자동 슬롯 추가 + hasImages='yes' 설정
- [x] VPS 배포 + PM2 재시작

### Next Actions
1. [ ] n8n ao-produce 웹훅 워크플로우 활성화 + E2E 테스트
2. [ ] 이미지 생성 E2E 테스트 (kie.ai API 키 필요)
3. [ ] Cloudflare Pages 프론트엔드 빌드 확인

## E) Blockers / Issues
- **Blockers**: n8n ao-produce 웹훅 워크플로우 활성화 필요
- **Known Issues**: 없음

## F) 변경 파일
- productions-client.tsx (자동 import useEffect 추가, +22줄)

## G) 다음 세션 시작용 메시지 (복붙용)
> 이미지 생성 → 영상 제작 자동 연동 완료 + VPS 배포. n8n 웹훅 E2E 테스트 필요.
