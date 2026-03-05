# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.

---

## A) 상태 요약
- **워크스페이스**: ~/n8n-worktrees/web (feature/web-app)
- **브랜치**: feature/web-app
- **Current Status**: 슬라이드쇼 UI 개편 완료 (20장 + 선택지 3가지) + VPS 배포 완료
- **Goal**: n8n ao-produce 웹훅 E2E 테스트

## B) 환경/의존성
- **서버**: VPS 76.13.182.180
- **환경**: Local + Prod
- **Required Secrets**: packages/backend/.env (VPS: /root/n8n-web/packages/backend/.env)
- **VPS_HOST**: 76.13.182.180 (.env에 추가됨)

## C) 마지막 실행 기록
- **Last Run Command**:
  ```
  VPS: git pull + tsc + pm2 restart
  ```
- **Result**: PASS - PM2 online, quality-check PASS
- **실행 위치**: VPS (SSH)
- **Last Commit**: `8426e53 feat: 슬라이드쇼 UI 개편 (20장 + 선택지 3가지)`

## D) 완료/미완료

### Done
- [x] 슬라이드쇼 UI: 이미지 있어?/없어? 선택
- [x] 슬라이드쇼: 칸 3개 초기 → [+추가] 1칸씩 → 최대 20장
- [x] 슬라이드쇼: 파일별 선택지 3가지 (직접 사용 / 새 이미지 생성 / 분석만 반영)
- [x] 분석만 반영: 자동 프롬프트 표시 + 수정 가능 textarea
- [x] 이미지 표시 시간 선택 제거 (나레이션 길이로 자동 결정)
- [x] 프롬프트 필수 입력 (슬라이드쇼 모드)
- [x] SlideshowSlotCard 컴포넌트 추가
- [x] 백엔드 files[] 타입에 use_mode, auto_prompt 추가
- [x] 기존 영상화 UI 변경 없음
- [x] VPS 배포 + PM2 재시작

### Next Actions
1. [ ] n8n ao-produce 웹훅 워크플로우 활성화 + E2E 테스트
2. [ ] 영상 제작 완료 후 미리보기 확인
3. [ ] Cloudflare Pages 프론트엔드 빌드 확인

## E) Blockers / Issues
- **Blockers**: n8n ao-produce 웹훅 워크플로우 활성화 필요
- **Known Issues**: 없음

## F) 변경 파일
- productions-client.tsx (슬라이드쇼 UI + SlideshowSlotCard)
- productions.ts (files[] use_mode, auto_prompt 타입 추가)

## G) 다음 세션 시작용 메시지 (복붙용)
> 슬라이드쇼 UI 개편 완료 (20장+선택지3가지). n8n ao-produce 웹훅 E2E 테스트 필요.
