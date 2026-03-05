# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.

---

## A) 상태 요약
- **워크스페이스**: ~/n8n-worktrees/web (feature/web-app)
- **브랜치**: feature/web-app
- **Current Status**: 전체 영상 제작 UI 개편 완료 (슬라이드쇼+영상화 한 페이지 통합)
- **Goal**: VPS 배포 + n8n ao-produce 웹훅 E2E 테스트

## B) 환경/의존성
- **서버**: VPS 76.13.182.180
- **환경**: Local + Prod
- **Required Secrets**: packages/backend/.env (VPS: /root/n8n-web/packages/backend/.env)
- **VPS_HOST**: 76.13.182.180 (.env에 추가됨)

## C) 마지막 실행 기록
- **Last Run Command**:
  ```
  Local: npx tsc --noEmit (frontend + backend) → PASS
  Local: scripts/quality-check.sh → PASS
  ```
- **Result**: PASS - TypeScript + quality-check 통과
- **실행 위치**: Local
- **Last Commit**: `2c1cbda feat: 전체 영상 제작 UI 개편 (슬라이드쇼+영상화 통합)`

## D) 완료/미완료

### Done
- [x] 탭 네비게이션(Step1/Step2) 제거 → 단일 페이지 플로우
- [x] "이미지가 있나요?" 분기: 있으면 업로드 슬롯, 없으면 AI 생성
- [x] AI 이미지 생성 UI (프롬프트 + 수량 선택 + 미리보기 + 수락/재생성)
- [x] SlotCard 통합 컴포넌트 (이미지: 3가지 선택지, 영상: 간단 프리뷰)
- [x] FileCard + SlideshowSlotCard → SlotCard로 통합
- [x] refFiles/uploadedFiles/slideshowSlots → imageSlots/videoSlots 상태 단순화
- [x] 백엔드 has_images, generated_images 웹훅 payload 추가
- [x] TypeScript + quality-check PASS

### Next Actions
1. [ ] VPS 배포: `git pull + npm install + tsc + pm2 restart`
2. [ ] n8n ao-produce 웹훅 워크플로우 활성화 + E2E 테스트
3. [ ] Cloudflare Pages 프론트엔드 빌드 확인

## E) Blockers / Issues
- **Blockers**: n8n ao-produce 웹훅 워크플로우 활성화 필요
- **Known Issues**: 없음

## F) 변경 파일
- productions-client.tsx (전면 재작성: 탭→단일페이지, SlotCard 통합)
- productions.ts (has_images, generated_images 추가)

## G) 다음 세션 시작용 메시지 (복붙용)
> 전체 영상 제작 UI 개편 완료 (슬라이드쇼+영상화 한 페이지 통합). VPS 배포 + n8n ao-produce 웹훅 E2E 테스트 필요.
