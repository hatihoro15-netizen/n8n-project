# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.

---

## A) 상태 요약
- **워크스페이스**: ~/n8n-worktrees/web (feature/web-app)
- **브랜치**: feature/web-app
- **Current Status**: AO 워크플로우 정리 완료 (라이브365 1개만 표시)
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
  VPS DB: AO Producer → "라이브365" 이름 변경 + AO Worker 삭제
  ```
- **Result**: PASS - 워크플로우 목록에 "라이브365" 1개만 표시
- **실행 위치**: VPS (SSH + Prisma)
- **Last Commit**: `67ca37b feat: AO 영상 제작 UI 구조 변경 — 슬롯 → 통합 파일 업로드`

## D) 완료/미완료

### Done
- [x] 통합 드래그&드롭 파일 업로드 UI (이미지+영상, 유/무 토글)
- [x] 백엔드 files[] 배열 지원 (clips[] 하위호환)
- [x] AO Producer → "라이브365" 이름 변경
- [x] AO Worker 삭제 (내부용, 목록 노출 불필요)
- [x] 제작 목록 체크박스 + 필터 + 일괄 작업 + 별표
- [x] AO 파이프라인 연결 (POST /api/productions/ao + 폴링 + 영상 미리보기)
- [x] 워크플로우 선택 드롭다운

### Next Actions
1. [ ] n8n ao-produce 웹훅 워크플로우 활성화 + E2E 테스트
2. [ ] 영상 제작 완료 후 미리보기 확인
3. [ ] Cloudflare Pages 프론트엔드 빌드 확인

## E) Blockers / Issues
- **Blockers**: n8n ao-produce 웹훅 워크플로우 활성화 필요
- **Known Issues**: 없음

## F) 변경 파일
- VPS DB: workflows 테이블 (AO Producer→라이브365, AO Worker 삭제)

## G) 다음 세션 시작용 메시지 (복붙용)
> AO 워크플로우 정리 완료 (라이브365 1개). n8n ao-produce 웹훅 E2E 테스트 필요.
