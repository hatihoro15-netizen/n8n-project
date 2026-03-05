# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> ✅ 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.
> (여기엔 최신 상태/Next/LastRun/Blockers만 유지)

---

## A) 상태 요약
- **워크스페이스**: ~/n8n-worktrees/web (feature/web-app)
- **브랜치**: feature/web-app
- **Current Status**: 빠른 제작 폼 UI + MinIO 업로드 + VPS 배포 완료
- **Goal**: n8n make-video 웹훅 워크플로우 활성화 후 E2E 완성

## B) 환경/의존성
- **서버**: VPS 76.13.182.180
- **환경**: Local + Prod
- **Required Secrets**: packages/backend/.env (VPS: /root/n8n-web/packages/backend/.env)
- **추가된 의존성**: @aws-sdk/client-s3, @fastify/multipart (이미 등록)
- **MinIO**: admin / NcaMin10S3cure! (Docker env), bucket: arubto

## C) 마지막 실행 기록
- **Last Run Command**:
  ```
  curl -X POST http://localhost:3001/api/media/upload -H "Authorization: Bearer $TOKEN" -F "files=@/tmp/test-upload.png"
  ```
- **Result**: PASS - MinIO arubto/uploads/ 에 파일 저장 확인
- **실행 위치**: VPS (SSH)
- **Last Commit**: `feat: add quick production form with MinIO image upload`

## D) 완료/미완료

### Done ✅
- [x] 운영 시스템 파일 구축
- [x] productions-client.tsx 빠른 제작 폼 UI (prompt_p1, topic, keywords, category)
- [x] 이미지 첨부 (드래그앤드롭 + 클릭, 최대 4장, 미리보기 + 삭제)
- [x] 백엔드 POST /api/media/upload → MinIO (arubto) 엔드포인트
- [x] 프론트 → MinIO 업로드 → images[] URL → 웹훅 호출 로직
- [x] 사진 없을 때 use_media: "auto" 분기
- [x] VPS 배포 (npm install, tsc build, PM2 restart)
- [x] VPS .env에 MINIO_* 크레덴셜 추가
- [x] E2E: 이미지 업로드 → MinIO 저장 확인 (PASS)

### Next Actions ➡️ (우선순위 1~3)
1. [ ] n8n에서 make-video 웹훅 워크플로우 생성 + 활성화 (현재 404)
2. [ ] 웹훅 활성화 후 E2E 재테스트 (이미지 + auto 양쪽)
3. [ ] Cloudflare Pages 프론트엔드 배포 확인

## E) Blockers / Issues
- **Blockers**: n8n make-video 웹훅 워크플로우가 아직 미등록 (production/test URL 모두 404)
- **Known Issues**: 없음
- **롤백 필요 시**: git revert d73be60

## F) 변경 파일
- packages/frontend/src/app/(dashboard)/productions/productions-client.tsx
- packages/backend/src/routes/media.ts (MinIO 업로드 엔드포인트)
- packages/backend/src/server.ts (@fastify/multipart 등록)
- packages/backend/src/config.ts (MinIO 설정)
- packages/backend/package.json (@aws-sdk/client-s3)
- VPS /root/n8n-web/packages/backend/.env (MINIO_* 추가)

## G) 다음 세션 시작용 메시지 (복붙용)
> 빠른 제작 폼 + MinIO 업로드 배포 완료. n8n make-video 웹훅 워크플로우 생성/활성화 필요 (현재 404).
