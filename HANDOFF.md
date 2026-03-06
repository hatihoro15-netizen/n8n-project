# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.

---

## A) 상태 요약
- **워크스페이스**: ~/n8n-worktrees/web (feature/web-app)
- **브랜치**: feature/web-app
- **Current Status**: 이미지 개별 선택 + 다운로드 기능 추가 + VPS 배포 완료
- **Goal**: 브라우저 E2E 테스트

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
  VPS: git pull origin feature/web-app (프론트엔드만 변경, 백엔드 재시작 불필요)
  ```
- **Result**: PASS - PM2 online
- **실행 위치**: VPS (SSH)
- **Last Commit**: `f58145f feat: 이미지 개별 선택 + 다운로드 기능 추가`

## D) 완료/미완료

### Done
- [x] 이미지 생성 페이지: 체크박스 선택 + 다운로드 + 선택한 이미지만 영상 제작 전송
- [x] 영상 제작 페이지: 생성 이미지 체크박스 + 다운로드 + 선택한 이미지만 슬롯 추가
- [x] VPS 배포 완료

### Next Actions
1. [ ] 브라우저에서 이미지 생성 E2E 테스트 (프롬프트만 / 참조이미지 / 내사진)
2. [ ] ao-produce 웹훅 500 해결 (n8n 워크플로우 내부 문제)
3. [ ] 전체 플로우 E2E (로그인 → 이미지 생성 → 선택 → 영상 제작)

## E) Blockers / Issues
- **Blockers**: ao-produce 웹훅 500 (n8n 워크플로우 내부 실행 실패)
- **Known Issues**: 없음

## F) 변경 파일
- images-client.tsx (체크박스 + 다운로드 + 통합 영상제작 버튼)
- productions-client.tsx (generatedImages 객체 배열 + 체크박스 + 다운로드)

## G) 다음 세션 시작용 메시지 (복붙용)
> 이미지 선택 + 다운로드 추가 완료. VPS 배포됨. 브라우저 E2E 테스트 필요. ao-produce 500 (n8n 내부).
