# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.

---

## A) 상태 요약
- **워크스페이스**: ~/n8n-worktrees/web (feature/web-app)
- **브랜치**: feature/web-app
- **Current Status**: Whisk 스타일 2탭 UI + VPS 배포 완료
- **Goal**: VPS .env에 KIEAI_API_KEY / CLAUDE_API_KEY 추가 후 E2E 검증

## B) 환경/의존성
- **서버**: VPS 76.13.182.180
- **환경**: Local + Prod
- **Required Secrets**: packages/backend/.env (VPS: /root/n8n-web/packages/backend/.env)
- **추가된 의존성**: @aws-sdk/client-s3, @fastify/multipart (이미 등록)
- **MinIO**: admin / NcaMin10S3cure! (Docker env), bucket: arubto

## C) 마지막 실행 기록
- **Last Run Command**:
  ```
  ssh root@76.13.182.180 'cd /root/n8n-web && pm2 restart deploy/ecosystem.config.js'
  ```
- **Result**: PASS - Backend online at 0.0.0.0:3001
- **실행 위치**: VPS (SSH)
- **Last Commit**: `d9d32b7 feat: Whisk 스타일 이미지 생성 + 영상 제작 UI`

## D) 완료/미완료

### Done
- [x] 운영 시스템 파일 구축
- [x] Whisk 스타일 2탭 UI (Step 1: 이미지 생성, Step 2: 영상 제작)
- [x] Step 1: kie.ai 이미지 생성 + 참고 이미지 (subject/scene/style)
- [x] Step 2: 10슬롯 그리드 + Claude Vision 자동 분석 + 개별 프롬프트
- [x] 최종 프롬프트 = Vision 분석 + 개별 프롬프트 + 메인 P1 조합
- [x] 웹훅 URL: ao-produce
- [x] 백엔드: generate-image, analyze-image, media proxy, upload 엔드포인트
- [x] VPS 배포 (npm install, tsc build, PM2 restart)

### Next Actions
1. [ ] VPS .env에 KIEAI_API_KEY, CLAUDE_API_KEY 추가 (사용자가 키 제공 필요)
2. [ ] n8n에서 ao-produce 웹훅 워크플로우 생성 + 활성화
3. [ ] E2E 테스트: 이미지 생성 → Vision 분석 → 영상 제작 웹훅 호출
4. [ ] Cloudflare Pages 프론트엔드 배포 확인

## E) Blockers / Issues
- **Blockers**: VPS .env에 KIEAI_API_KEY / CLAUDE_API_KEY 미설정 (이미지 생성/분석 501 응답)
- **Known Issues**: n8n ao-produce 웹훅 워크플로우 미등록 (404 예상)

## F) 변경 파일
- packages/frontend/src/app/(dashboard)/productions/productions-client.tsx (Whisk UI 전체 재작성)
- packages/backend/src/routes/media.ts (generate-image, analyze-image, proxy 추가)
- packages/backend/src/config.ts (kieai, claude 설정 추가)

## G) 다음 세션 시작용 메시지 (복붙용)
> Whisk 스타일 2탭 UI + VPS 배포 완료. KIEAI_API_KEY/CLAUDE_API_KEY .env 추가 + n8n ao-produce 웹훅 활성화 필요.
