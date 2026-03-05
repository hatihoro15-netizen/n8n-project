# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.

---

## A) 상태 요약
- **워크스페이스**: ~/n8n-worktrees/web (feature/web-app)
- **브랜치**: feature/web-app
- **Current Status**: Step1/Step2 UI 개편 완료 + VPS 배포 완료
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
- **Result**: PASS - PM2 online
- **실행 위치**: VPS (SSH)
- **Last Commit**: `d6274af feat: Step1 참조이미지 유/무+분석 + Step2 이미지/영상 분리 업로드`

## D) 완료/미완료

### Done
- [x] Step1: 참조 이미지 최대 5장, 유/무 토글, Vision 자동 분석, 선택적 프롬프트
- [x] Step2: 이미지(max 5) / 영상(max 5) 분리 업로드 영역
- [x] analyzeFileInState() 리팩토링 (ref/prod 타겟 분리)
- [x] 백엔드 ref_files[] 지원 추가
- [x] prompt_p1 선택적(optional)으로 변경
- [x] 영상 제작 방식 선택: 영상화 (Kling AI) / 슬라이드쇼
- [x] IP 하드코딩 → VPS_HOST 환경변수 전환
- [x] VPS 배포 + PM2 재시작

### Next Actions
1. [ ] n8n ao-produce 웹훅 워크플로우 활성화 + E2E 테스트
2. [ ] 영상 제작 완료 후 미리보기 확인
3. [ ] Cloudflare Pages 프론트엔드 빌드 확인

## E) Blockers / Issues
- **Blockers**: n8n ao-produce 웹훅 워크플로우 활성화 필요
- **Known Issues**: 없음

## F) 변경 파일
- productions-client.tsx (Step1 참조이미지 + Step2 이미지/영상 분리)
- productions.ts (ref_files[] 지원, prompt_p1 optional)

## G) 다음 세션 시작용 메시지 (복붙용)
> Step1 참조이미지(유/무+분석) + Step2 이미지/영상 분리 업로드 완료. n8n ao-produce 웹훅 E2E 테스트 필요.
