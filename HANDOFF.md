# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.

---

## A) 상태 요약
- **워크스페이스**: ~/n8n-worktrees/web (feature/web-app)
- **브랜치**: feature/web-app
- **Current Status**: AO 파이프라인 연결 + 워크플로우 선택 + 라이브365 AO 워크플로우 추가 완료
- **Goal**: n8n ao-produce 웹훅 E2E 테스트

## B) 환경/의존성
- **서버**: VPS 76.13.182.180
- **환경**: Local + Prod
- **Required Secrets**: packages/backend/.env (VPS: /root/n8n-web/packages/backend/.env)
- **추가된 의존성**: @aws-sdk/client-s3, @fastify/multipart (이미 등록)
- **MinIO**: admin / NcaMin10S3cure! (Docker env), bucket: arubto
- **KIEAI_API_KEY**: 설정 완료
- **CLAUDE_API_KEY**: 설정 완료

## C) 마지막 실행 기록
- **Last Run Command**:
  ```
  VPS node seed: 라이브365 채널 + AO Producer/Worker 워크플로우 INSERT
  ```
- **Result**: PASS - Channel created + AO Producer + AO Worker 모두 생성 확인
- **실행 위치**: VPS (SSH)
- **Last Commit**: `23b2328 feat: 라이브365 AO 워크플로우 목록 추가`

## D) 완료/미완료

### Done
- [x] Whisk 스타일 2탭 UI (이미지 생성 + 영상 제작)
- [x] 슬롯별 include_audio 체크박스
- [x] VPS API 키 설정 (KIEAI + CLAUDE)
- [x] 제작 목록 체크박스 + 필터 + 일괄 작업 + 별표
- [x] 캐릭터 카드 프로필 이미지
- [x] AO 파이프라인 연결 (POST /api/productions/ao + 폴링 + 영상 미리보기)
- [x] 워크플로우 선택 드롭다운 (Step 2)
- [x] 라이브365 채널 + AO Producer/Worker DB 추가
- [x] WorkflowType enum에 'ao' 추가

### Next Actions
1. [ ] n8n ao-produce 웹훅 워크플로우 활성화 + E2E 테스트
2. [ ] 영상 제작 완료 후 미리보기 확인
3. [ ] Cloudflare Pages 프론트엔드 빌드 확인

## E) Blockers / Issues
- **Blockers**: n8n ao-produce 웹훅 워크플로우 활성화 필요 (현재 웹훅 호출 시 실패 가능)
- **Known Issues**: 없음

## F) 변경 파일
- packages/backend/prisma/schema.prisma (WorkflowType enum에 'ao' 추가)
- packages/shared/src/index.ts (WorkflowType에 'ao' 추가)
- packages/backend/src/routes/productions.ts (POST /api/productions/ao)
- productions-client.tsx (워크플로우 선택 + 폴링 + JobStatusBadge)
- VPS DB: channels (라이브365), workflows (AO Producer, AO Worker)

## G) 다음 세션 시작용 메시지 (복붙용)
> AO 파이프라인 + 라이브365 워크플로우 완료. n8n ao-produce 웹훅 E2E 테스트 필요.
