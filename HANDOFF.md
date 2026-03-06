# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.

---

## A) 상태 요약
- **워크스페이스**: ~/n8n-worktrees/web (feature/web-app)
- **브랜치**: feature/web-app
- **Current Status**: 이미지 생성 페이지 추가 완료 (Whisk 방식) + VPS 배포 완료
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
- **Last Commit**: `a6b4344 feat: 이미지 생성 페이지 추가 (Whisk 방식)`

## D) 완료/미완료

### Done
- [x] /images 이미지 생성 페이지 신규 (Whisk 3슬롯: Subject/Scene/Style)
- [x] 사이드바 "이미지 생성" 메뉴 추가
- [x] 숏폼/롱폼 선택 + 프롬프트 + 생성 개수
- [x] kie.ai generate-image에 aspect_ratio 파라미터 추가
- [x] /api/media/save-external 엔드포인트 추가 (외부 이미지 → MinIO)
- [x] 결과 그리드: 저장/재생성/영상제작으로보내기
- [x] VPS 배포 + PM2 재시작

### Next Actions
1. [ ] n8n ao-produce 웹훅 워크플로우 활성화 + E2E 테스트
2. [ ] 이미지 생성 E2E 테스트 (kie.ai API 키 필요)
3. [ ] Cloudflare Pages 프론트엔드 빌드 확인

## E) Blockers / Issues
- **Blockers**: n8n ao-produce 웹훅 워크플로우 활성화 필요
- **Known Issues**: "영상 제작으로 보내기" → localStorage에 URL 저장 + /productions 이동까지만 구현 (자동 슬롯 추가는 productions 페이지 수정 필요)

## F) 변경 파일
- packages/frontend/src/app/(dashboard)/images/page.tsx (신규)
- packages/frontend/src/app/(dashboard)/images/images-client.tsx (신규)
- packages/frontend/src/components/layout/sidebar.tsx (메뉴 추가)
- packages/backend/src/routes/media.ts (aspect_ratio + save-external)

## G) 다음 세션 시작용 메시지 (복붙용)
> 이미지 생성 페이지 (Whisk 방식) + VPS 배포 완료. n8n 웹훅 E2E 테스트 필요.
