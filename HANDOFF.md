# HANDOFF.md — 세션 스냅샷 (항상 전체 Overwrite)

> 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.

---

## A) 상태 요약
- **워크스페이스**: ~/n8n-worktrees/web (feature/web-app)
- **브랜치**: feature/web-app
- **Current Status**: Whisk 2탭 UI + include_audio 체크박스 + VPS 배포 완료 + KIEAI_API_KEY 설정 완료
- **Goal**: CLAUDE_API_KEY 추가 + n8n ao-produce 웹훅 활성화 + E2E 검증

## B) 환경/의존성
- **서버**: VPS 76.13.182.180
- **환경**: Local + Prod
- **Required Secrets**: packages/backend/.env (VPS: /root/n8n-web/packages/backend/.env)
- **추가된 의존성**: @aws-sdk/client-s3, @fastify/multipart (이미 등록)
- **MinIO**: admin / NcaMin10S3cure! (Docker env), bucket: arubto
- **KIEAI_API_KEY**: 설정 완료 (VPS .env)
- **CLAUDE_API_KEY**: 미설정 (Vision 분석 501 예상)

## C) 마지막 실행 기록
- **Last Run Command**:
  ```
  curl -X POST http://localhost:3001/api/media/generate-image -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"prompt":"test","count":1}'
  ```
- **Result**: PASS - HTTP 200, {"success":true,"data":{"images":[]}} (501 아님, API 키 정상)
- **실행 위치**: VPS (SSH)
- **Last Commit**: `c656534 feat: 슬롯별 include_audio 체크박스 추가 + API 키 설정`

## D) 완료/미완료

### Done
- [x] Whisk 스타일 2탭 UI (Step 1: 이미지 생성, Step 2: 영상 제작)
- [x] 슬롯별 include_audio 체크박스 ("나레이션/대사 포함")
- [x] 웹훅 payload: clips[] 형식 (image_url, vision_analysis, scene_prompt, include_audio)
- [x] VPS .env에 KIEAI_API_KEY 추가 → generate-image 501 해소 (200 정상)
- [x] VPS 배포 (PM2 online)

### Next Actions
1. [ ] VPS .env에 CLAUDE_API_KEY 추가 (Vision 분석용, 사용자가 키 제공 필요)
2. [ ] n8n에서 ao-produce 웹훅 워크플로우 생성 + 활성화
3. [ ] E2E 테스트: 이미지 생성 → Vision 분석 → 영상 제작 웹훅 호출
4. [ ] Cloudflare Pages 프론트엔드 배포 확인

## E) Blockers / Issues
- **Blockers**: CLAUDE_API_KEY 미설정 (Vision 분석 501 예상), n8n ao-produce 웹훅 미등록 (404)
- **Known Issues**: generate-image가 200 리턴하나 images[] 빈 배열 (kie.ai 태스크 타임아웃 가능성 — 실제 프롬프트로 재테스트 필요)

## F) 변경 파일
- packages/frontend/src/app/(dashboard)/productions/productions-client.tsx (include_audio 체크박스, clips[] payload)
- VPS /root/n8n-web/packages/backend/.env (KIEAI_API_KEY 추가)

## G) 다음 세션 시작용 메시지 (복붙용)
> include_audio 체크박스 + KIEAI_API_KEY 설정 완료. CLAUDE_API_KEY 추가 + n8n ao-produce 웹훅 활성화 필요.
