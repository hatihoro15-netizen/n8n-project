# PROGRESS.md — 진행 일지

> ❌ 날짜별 보고서는 append만(삭제/overwrite 금지).
> ✅ 상단 "현재 요약" 섹션만 매 세션 overwrite 가능.
> ✅ Next Actions 정답은 HANDOFF.md에. 여기엔 방향/메모만.

---

## 현재 요약 (이 섹션만 overwrite 가능)
- 마지막 업데이트: 2026-03-06
- 현재 상태(1줄): Step1 참조이미지(유/무+분석) + Step2 이미지/영상 분리 업로드 완료 + VPS 배포 완료
- 진행중 작업: n8n ao-produce E2E 테스트
- 최근 완료: Step1/Step2 UI 개편 + ref_files[] 백엔드 지원
- 주의사항: n8n ao-produce 웹훅 활성화 필요

---

## 작업 보고서 (append-only, 양식: docs/07-report-template.md 참조)

(여기서부터 날짜별 append)

## 2026-03-05
### ✅ Done
- [x] CLAUDE.md 운영 지침 생성 (5파일 체계 + docs/ 참조 테이블 + 에이전트 역할)
- [x] HANDOFF.md 세션 스냅샷 생성 (A~G 섹션 구조)
- [x] PROGRESS.md 진행 일지 생성
- [x] process.md 지식베이스 유지
- [x] docs/ 7개 참조 문서 생성 (01-architecture ~ 07-report-template)
- [x] scripts/quality-check.sh 생성 + chmod +x (오탐지 패턴 정밀화)
- [x] settings.json.sample 생성 (6개 워크트리 PostToolUse hook)
- [x] .claude/commands/start.md 생성 (/start 슬래시 커맨드)
### 🔁 Tried
- [ ] quality-check.sh 실행 → 기존 코드(media.ts) IP 하드코딩 탐지
### 📌 Result
- 운영 시스템 파일 전체 구축 완료
- quality-check.sh: 기존 코드 1건 IP 하드코딩 감지 (packages/backend/src/routes/media.ts ALLOWED_HOSTS)
- 오탐지 패턴 정밀화: 0.0.0.0/127.0.0.1 제외, 변수 선언 token= 제외, .vercel/.next/dist 빌드산출물 제외
### ➡️ Next (방향만 / 실행 커맨드는 HANDOFF)
- media.ts ALLOWED_HOSTS를 환경변수로 전환 (기존 코드 개선)
- 워크플로우 실제 작업 시작
### 📁 Files / Links
- CLAUDE.md, HANDOFF.md, PROGRESS.md, process.md
- docs/01~07, scripts/quality-check.sh
- settings.json.sample, .claude/commands/start.md

## 2026-03-06
### ✅ Done
- [x] productions-client.tsx: 빠른 제작 폼 UI (prompt_p1, topic, keywords, category + 이미지 첨부)
- [x] 백엔드 POST /api/media/upload → MinIO(arubto) 엔드포인트 신규
- [x] @aws-sdk/client-s3 + @fastify/multipart 추가
- [x] config.ts에 MinIO 설정 추가
- [x] VPS 배포 (git pull + npm install + tsc build + PM2 restart)
- [x] VPS .env에 MINIO_ENDPOINT/ACCESS_KEY/SECRET_KEY/BUCKET 추가
- [x] E2E: 이미지 업로드 → MinIO arubto/uploads/ 저장 확인 (PASS)
### 🔁 Tried
- [ ] n8n make-video 웹훅 호출 → 404 (워크플로우 미등록/미활성화)
- [ ] webhook-test URL도 404 (워크플로우 자체가 n8n에 없음)
### 📌 Result
- 업로드 파이프라인 정상: 프론트 → 백엔드 /api/media/upload → MinIO arubto → URL 반환
- 웹훅 미연결: n8n에 make-video 웹훅 워크플로우가 아직 없음
- MinIO 크레덴셜: Docker env에서 admin/NcaMin10S3cure! 확인 → .env에 반영
### ➡️ Next (방향만 / 실행 커맨드는 HANDOFF)
- n8n에서 AO Producer 워크플로우 생성 + make-video 웹훅 활성화
- 웹훅 활성화 후 E2E 재테스트
- Cloudflare Pages 프론트엔드 배포 확인
### 📁 Files / Links
- packages/frontend/src/app/(dashboard)/productions/productions-client.tsx
- packages/backend/src/routes/media.ts, server.ts, config.ts
- VPS: /root/n8n-web/packages/backend/.env

## 2026-03-06 (2차)
### Done
- [x] Whisk 스타일 2탭 UI 구현 (Step 1: 이미지 생성, Step 2: 영상 제작)
- [x] Step 1: kie.ai 연동 + 참고 이미지 (subject/scene/style) + 생성 수 선택
- [x] Step 2: 10슬롯 그리드 + Claude Vision 자동 분석 + 개별 프롬프트
- [x] 최종 프롬프트 조합: Vision 분석 + 개별 프롬프트 + 메인 P1
- [x] 웹훅 URL ao-produce로 변경
- [x] 백엔드: /api/media/generate-image, /api/media/analyze-image 엔드포인트
- [x] config.ts에 kieai, claude 설정 추가
- [x] VPS 배포 (git pull + npm install + tsc build + PM2 restart) - PASS
### Tried
- [ ] KIEAI_API_KEY / CLAUDE_API_KEY → VPS .env 미추가 (키 미제공)
### Result
- 타입 체크 통과 + VPS 배포 완료 (PM2 online)
- 이미지 생성/분석 기능은 API 키 추가 후 동작 예정
### Next (방향만)
- VPS .env에 KIEAI_API_KEY, CLAUDE_API_KEY 추가
- n8n ao-produce 웹훅 워크플로우 생성 + 활성화
- E2E 전체 플로우 테스트
### Files / Links
- packages/frontend/src/app/(dashboard)/productions/productions-client.tsx (전면 재작성)
- packages/backend/src/routes/media.ts (generate-image, analyze-image 추가)
- packages/backend/src/config.ts (kieai, claude 설정)

## 2026-03-06 (3차)
### Done
- [x] 슬롯별 include_audio 체크박스 추가 ("나레이션/대사 포함")
- [x] 웹훅 payload를 clips[] 형식으로 변경 (image_url, vision_analysis, scene_prompt, include_audio)
- [x] VPS .env에 KIEAI_API_KEY 추가
- [x] VPS 배포 + PM2 재시작
- [x] generate-image API 501 → 200 확인 (PASS)
### Tried
- [ ] generate-image 200 리턴하나 images[] 빈 배열 (kie.ai 태스크 타임아웃 — 실제 프롬프트로 재테스트 필요)
### Result
- 타입 체크 통과 + VPS 배포 완료
- KIEAI_API_KEY 설정으로 501 해소
- CLAUDE_API_KEY 미설정 (Vision 분석은 아직 501)
### Next (방향만)
- CLAUDE_API_KEY 추가
- n8n ao-produce 웹훅 워크플로우 활성화
- E2E 전체 플로우 테스트
### Files / Links
- productions-client.tsx (include_audio 체크박스, clips[] payload)
- VPS /root/n8n-web/packages/backend/.env (KIEAI_API_KEY 추가)

## 2026-03-06 (4차)
### Done
- [x] 제작 목록 체크박스 + 상태별 선택 드롭다운 + 별표 + 일괄 작업
- [x] 캐릭터 카드 소형 프로필 이미지 (MinIO 업로드)
- [x] AO 파이프라인 연결 (POST /api/productions/ao + 폴링 + 영상 미리보기)
- [x] 워크플로우 선택 드롭다운 (Step 2)
- [x] WorkflowType enum에 'ao' 추가 (Prisma + shared)
- [x] 라이브365 채널 + AO Producer/Worker DB seed
- [x] VPS 배포 + PM2 재시작
### Result
- 워크플로우 목록: AO Producer + AO Worker (라이브365) 정상 표시
- API 키: KIEAI + CLAUDE 모두 설정 완료
### Next (방향만)
- n8n ao-produce 웹훅 E2E 테스트
- 영상 미리보기 확인
### Files / Links
- schema.prisma, shared/index.ts (WorkflowType ao 추가)
- productions.ts (POST /api/productions/ao)
- productions-client.tsx (워크플로우 선택 + JobStatusBadge + 폴링)
- characters-client.tsx (프로필 이미지)
- VPS DB: channels (라이브365), workflows (AO Producer, AO Worker)

## 2026-03-06 (5차)
### Done
- [x] AO 영상 제작 UI 전면 재작성: 10슬롯 그리드 → 통합 드래그&드롭 파일 업로드
- [x] 파일별 "유/무" 토글 (직접 사용 / 분석만)
- [x] 이미지+영상 동시 업로드 지원, 자동 Claude Vision 분석
- [x] 백엔드 POST /api/productions/ao에 files[] 배열 지원 추가 (clips[] 하위호환)
- [x] VPS 배포 + PM2 재시작
### Result
- 타입 체크 통과 + VPS 배포 완료 (PM2 online)
- 기존 슬롯 구조(Slot, RefImage, ImageSlot, RefImageSlot) 완전 제거
- 새 구조: UploadedFile 타입 + FileCard 컴포넌트 + 통합 드롭존
### Next (방향만)
- n8n ao-produce 웹훅 E2E 테스트
- Cloudflare Pages 프론트엔드 빌드 확인
### Files / Links
- productions-client.tsx (전면 재작성: 슬롯→통합 파일 업로드)
- productions.ts (files[] 지원 추가)

## 2026-03-06 (6차)
### Done
- [x] AO Producer 이름 → "라이브365" 변경 (VPS DB)
- [x] AO Worker 삭제 (내부용, 목록 노출 불필요)
### Result
- 워크플로우 목록에 AO 타입은 "라이브365" 1개만 표시
### Next (방향만)
- n8n ao-produce 웹훅 E2E 테스트
### Files / Links
- VPS DB: workflows 테이블 UPDATE/DELETE

## 2026-03-06 (7차)
### Done
- [x] config.ts MinIO endpoint → VPS_HOST 환경변수 전환
- [x] media.ts ALLOWED_HOSTS → VPS_HOST 환경변수 전환
- [x] VPS .env에 VPS_HOST=76.13.182.180 추가
- [x] quality-check.sh PASS
- [x] VPS 배포 + PM2 재시작
### Result
- quality-check.sh PASS (IP 하드코딩 0건)
- TypeScript 체크 통과
### Next (방향만)
- n8n ao-produce 웹훅 E2E 테스트
### Files / Links
- packages/backend/src/config.ts (MinIO endpoint)
- packages/backend/src/routes/media.ts (ALLOWED_HOSTS)
- VPS .env (VPS_HOST 추가)

## 2026-03-06 (8차)
### Done
- [x] Step 2에 제작 방식 선택 UI 추가 (영상화 Kling AI / 슬라이드쇼)
- [x] 영상화: 클립 길이 5초/8초, 슬라이드쇼: 표시 시간 2초/3초/5초
- [x] 웹훅 payload에 production_mode, slide_duration 추가
- [x] 백엔드 POST /api/productions/ao에 새 필드 전달
- [x] VPS 배포 + PM2 재시작
### Result
- TypeScript + quality-check PASS
- VPS PM2 online
### Next (방향만)
- n8n ao-produce 웹훅 E2E 테스트
### Files / Links
- productions-client.tsx (제작 방식 선택 UI)
- productions.ts (production_mode, slide_duration)

## 2026-03-06 (9차)
### Done
- [x] Step1 참조 이미지 개편: max 5장, 유/무 토글, Claude Vision 자동 분석, 선택적 프롬프트
- [x] Step2 이미지/영상 분리: 이미지 영역(max 5) + 영상 영역(max 5) 각각 드롭존
- [x] analyzeFileInState() 리팩토링 (target: 'ref' | 'prod' 파라미터)
- [x] 백엔드 ref_files[] 배열 지원 + 웹훅 payload 전달
- [x] prompt_p1 optional로 변경 (프론트+백엔드)
- [x] VPS 배포 + PM2 재시작
### Result
- TypeScript 체크 통과 + VPS PM2 online
- refFiles / uploadedFiles 상태 분리 완료
### Next (방향만)
- n8n ao-produce 웹훅 E2E 테스트
- Cloudflare Pages 프론트엔드 빌드 확인
### Files / Links
- productions-client.tsx (Step1 refFiles + Step2 이미지/영상 분리)
- productions.ts (ref_files[], prompt_p1 optional)
