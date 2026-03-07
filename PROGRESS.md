# PROGRESS.md — 진행 일지

> ❌ 날짜별 보고서는 append만(삭제/overwrite 금지).
> ✅ 상단 "현재 요약" 섹션만 매 세션 overwrite 가능.
> ✅ Next Actions 정답은 HANDOFF.md에. 여기엔 방향/메모만.

---

## 현재 요약 (이 섹션만 overwrite 가능)
- 마지막 업데이트: 2026-03-07
- 현재 상태(1줄): 미디어 선택 옵션 정리 완료 (generate 제거 + analysis_only 고도화)
- 진행중 작업: VPS 배포 + E2E 테스트
- 최근 완료: "새 이미지 생성" 옵션 제거, "분석만 반영" 프롬프트 수정 UI 개선
- 주의사항: kie.ai 크레딧 부족(402), PM2 프로세스명=n8n-web-backend

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

## 2026-03-06 (10차)
### Done
- [x] 슬라이드쇼 UI 개편: "이미지 있어?/없어?" 선택
- [x] 슬라이드쇼 이미지 업로드: 칸 3개 초기 → [+추가] 1칸씩 → 최대 20장
- [x] 파일별 선택지 3가지: 직접 사용 / 새 이미지 생성 / 분석만 반영
- [x] 분석만 반영 시 자동 프롬프트 표시 + 수정 가능
- [x] 이미지 표시 시간 선택 제거 (나레이션 길이로 자동 결정)
- [x] 슬라이드쇼 프롬프트 필수 입력
- [x] SlideshowSlotCard 컴포넌트 추가
- [x] 백엔드 files[] 타입에 use_mode, auto_prompt 추가
- [x] 기존 영상화 UI 변경 없음
- [x] VPS 배포 + PM2 재시작
### Result
- TypeScript + quality-check PASS
- VPS PM2 online
### Next (방향만)
- n8n ao-produce 웹훅 E2E 테스트
### Files / Links
- productions-client.tsx (슬라이드쇼 UI + SlideshowSlotCard)
- productions.ts (files[] use_mode, auto_prompt)

## 2026-03-06 (11차)
### Done
- [x] 전체 영상 제작 UI 개편: 탭(Step1/Step2) → 단일 페이지 플로우
- [x] "이미지가 있나요?" 분기: 있으면 업로드 슬롯, 없으면 AI 생성
- [x] AI 이미지 생성 UI: 프롬프트 + 수량(2/4/6/8) + 미리보기 그리드 + 수락/재생성
- [x] SlotCard 통합 컴포넌트: 이미지(3가지 선택지) + 영상(간단 프리뷰)
- [x] FileCard + SlideshowSlotCard → SlotCard 통합
- [x] refFiles/uploadedFiles/slideshowSlots → imageSlots/videoSlots 상태 단순화
- [x] 백엔드 has_images, generated_images 웹훅 payload 추가
### Result
- TypeScript + quality-check PASS
- 코드 567 추가, 691 삭제 (124줄 감소)
### Next (방향만)
- VPS 배포
- n8n ao-produce 웹훅 E2E 테스트
### Files / Links
- productions-client.tsx (전면 재작성)
- productions.ts (has_images, generated_images 추가)

## 2026-03-06 (12차)
### Done
- [x] VPS 배포: git pull + npm install + tsc + pm2 restart n8n-web-backend
### Result
- PM2 online, tsc 통과
- PM2 프로세스명: n8n-web-backend (n8n-backend 아님 주의)
### Next (방향만)
- n8n ao-produce 웹훅 E2E 테스트
### Files / Links
- VPS: /root/n8n-web (feature/web-app)

## 2026-03-06 (13차)
### Done
- [x] 숏폼/롱폼 선택 UI 추가 (워크플로우 선택 아래, 제작 방식 위)
- [x] 프론트 aspectRatio 상태 + 숏폼(9:16)/롱폼(16:9) 버튼
- [x] 백엔드 aspect_ratio body 타입 + 웹훅 payload 전달
- [x] VPS 배포 + PM2 재시작
### Result
- TypeScript + quality-check PASS
- VPS PM2 online
### Next (방향만)
- n8n ao-produce 웹훅 E2E 테스트
### Files / Links
- productions-client.tsx (aspectRatio 상태 + UI)
- productions.ts (aspect_ratio 타입 + payload)

## 2026-03-06 (14차)
### Done
- [x] /images 이미지 생성 페이지 신규 추가 (Whisk 방식)
- [x] 3슬롯 UI: 피사체(Subject) / 장면(Scene) / 스타일(Style)
- [x] 각 슬롯: 이미지 업로드 + Claude Vision 자동 분석 + 유/무 토글
- [x] 숏폼/롱폼 선택 + 프롬프트 (필수) + 생성 개수 (1/2/3)
- [x] kie.ai generate-image에 aspect_ratio 파라미터 추가
- [x] /api/media/save-external 엔드포인트 신규 (외부 이미지 → MinIO 저장)
- [x] 결과 그리드: 저장 / 재생성 / 영상 제작으로 보내기
- [x] 사이드바 "이미지 생성" 메뉴 추가 (Wand2 아이콘)
- [x] VPS 배포 + PM2 재시작
### Result
- TypeScript + quality-check PASS
- VPS PM2 online
- "영상 제작으로 보내기": localStorage 저장 + 페이지 이동까지 (자동 슬롯 추가는 별도)
### Next (방향만)
- n8n ao-produce 웹훅 E2E 테스트
- 이미지 생성 E2E 테스트
### Files / Links
- packages/frontend/src/app/(dashboard)/images/page.tsx (신규)
- packages/frontend/src/app/(dashboard)/images/images-client.tsx (신규)
- packages/frontend/src/components/layout/sidebar.tsx (메뉴 추가)
- packages/backend/src/routes/media.ts (aspect_ratio + save-external)

## 2026-03-06 (15차)
### Done
- [x] 이미지 생성 → 영상 제작 자동 연동
- [x] WhiskProductionForm 마운트 시 localStorage 확인 → imageSlots 자동 추가
- [x] hasImages='yes' 자동 설정
- [x] VPS 배포 + PM2 재시작
### Result
- TypeScript + quality-check PASS
- VPS PM2 online
### Next (방향만)
- n8n ao-produce 웹훅 E2E 테스트
### Files / Links
- productions-client.tsx (+22줄, 자동 import 로직)

## 2026-03-06 (16차)
### Done
- [x] Cloudflare Pages 프론트엔드 빌드 성공 (모든 페이지 정상)
- [x] GET /api/productions/:id/status 경량 상태 조회 엔드포인트 추가
- [x] 폴링 간격 10초 → 2초 (경량 API 사용)
- [x] JobProgressBar 컴포넌트: 상태별 퍼센트 바 (0~100%)
- [x] failed 시 재시도 버튼 추가
- [x] VPS 배포 + PM2 재시작
### Result
- TypeScript + quality-check + 빌드 PASS
- VPS PM2 online
### Next (방향만)
- n8n ao-produce 웹훅 E2E 테스트
- Cloudflare Pages 실제 배포 트리거
### Files / Links
- productions-client.tsx (JobProgressBar + 2초 폴링 + 재시도)
- productions.ts (GET /api/productions/:id/status)

## 2026-03-06 (17차)
### Done
- [x] CF Pages 배포 상태 확인: 메인 페이지 정상 렌더링 (타이틀, 메타 확인)
- [x] 로컬 build:cf 실행: 15개 Edge Function Routes 성공 (/images 포함)
### Tried
- [ ] WebFetch로 페이지 확인 → 404처럼 보임 (JS 미실행으로 인한 오탐)
- [x] curl HTTP 상태코드 확인 → 모든 페이지 200 OK
### Result
- CF Pages 배포 정상: /, /productions, /images, /login 모두 HTTP 200
- WebFetch는 JS를 실행하지 않아 Next.js CSR 페이지를 404로 오인함
- 실제 브라우저에서는 정상 렌더링
### Next (방향만)
- n8n ao-produce 웹훅 E2E 테스트
### Files / Links
- wrangler.toml: packages/frontend/wrangler.toml
- build:cf: `npx @cloudflare/next-on-pages`

## 2026-03-06 (18차)
### Done
- [x] 버그1: 프롬프트만으로 이미지 생성 버튼 활성화 (activeSlots.length > 0 조건 제거)
- [x] 버그2: generate-image를 n8n ao-generate-image 웹훅으로 전환 (kie.ai 직접 호출 제거)
- [x] 내 사진으로 만들기 섹션 추가 (접기/펴기, 최대 10장, Claude Vision, 3가지 모드)
- [x] triggerWebhook에 res.ok 체크 추가 (에러 핸들링 개선)
- [x] ao-generate-image 웹훅 E2E 테스트 PASS (200 + 이미지 URL 반환)
- [x] VPS 배포 + PM2 재시작
### Tried
- [x] ao-produce 웹훅 → 500 (n8n 워크플로우 내부 실행 실패, 웹훅 연결 자체는 정상)
### Result
- ao-generate-image: 200 + images 배열 반환 (정상)
- ao-produce: 500 (n8n 워크플로우 내부 문제, 웹앱→n8n 연결은 정상)
- TypeScript + VPS 배포 PASS
### Next (방향만)
- 브라우저에서 이미지 생성 E2E 테스트
- ao-produce n8n 워크플로우 디버깅
### Files / Links
- packages/frontend/src/app/(dashboard)/images/images-client.tsx (버그 수정 + 내 사진 섹션)
- packages/backend/src/routes/media.ts (kie.ai → n8n webhook)
- packages/backend/src/utils/n8n-client.ts (에러 핸들링)

## 2026-03-06 (19차)
### Done
- [x] 이미지 생성 페이지: 체크박스 선택 + 다운로드 + 선택한 이미지만 영상 제작 전송
- [x] 영상 제작 페이지: 생성 이미지 체크박스 + 다운로드 + 선택한 이미지만 슬롯 추가
- [x] generatedImages: string[] → {url, selected}[] 객체 배열로 변경
- [x] VPS 배포 (git pull만, 백엔드 변경 없음)
### Result
- TypeScript PASS
- VPS PM2 online
### Next (방향만)
- 브라우저 E2E 테스트
- ao-produce n8n 워크플로우 디버깅
### Files / Links
- images-client.tsx (체크박스 + 다운로드 + 통합 영상제작 버튼)
- productions-client.tsx (generatedImages 객체 배열 + 체크박스 + 다운로드)

## 2026-03-06 (20차)
### Done
- [x] topic/keywords/category 400 에러 수정 (|| undefined 제거 → 빈 문자열 전달)
- [x] 프론트: ref_subject/ref_scene/ref_style → slots 객체 {use, url, vision_analysis} 형식 전환
- [x] 백엔드: slots + my_images 타입 정의 + n8n 웹훅 그대로 전달
- [x] n8n Code 노드 "이미지 생성" 업데이트:
  - slots.subject/scene/style의 url → kie.ai subject/scene/style_image_url로 전달
  - slots vision_analysis → 프롬프트 파트로 추가
  - my_images 배열 처리 (analysis_only → auto_prompt, generate → analysis, direct → subject 폴백)
- [x] n8n 워크플로우 백업 저장 (/root/n8n-web/backup-ao-generate-image.json)
- [x] VPS 배포 (git pull + tsc + pm2 restart)
### Tried
- [x] slots + my_images 포함 이미지 생성 요청 → n8n 데이터 정상 수신 확인
- [ ] kie.ai → 402 Credits insufficient (크레딧 부족, 코드 문제 아님)
### Result
- 3계층(프론트→백엔드→n8n) 데이터 구조 일치 확인
- n8n 실행 로그에서 slots/my_images 정상 파싱 확인
- kie.ai 크레딧 부족으로 실제 이미지 생성 미검증
### Next (방향만)
- kie.ai 크레딧 충전 후 E2E 검증
- ao-produce 500 n8n 워크플로우 디버깅
### Files / Links
- images-client.tsx (slots 객체 전송)
- media.ts (slots + my_images 타입 + 웹훅 전달)
- productions-client.tsx (|| undefined 제거)
- n8n workflow d5b35fb7f1724e448 (Code 노드 업데이트)

## 2026-03-06 (21차)
### Done
- [x] 나레이션 방식 선택 UI 추가 (AI 자동 생성 / 직접 입력 라디오)
- [x] AI 자동 생성 선택 시 안내 텍스트 박스 표시
- [x] 직접 입력 선택 시 textarea 표시
- [x] payload에 narration_mode, narration_text 추가
- [x] 직접 사용 선택 시 제작 방식 자동 영상화(Kling AI) 전환
- [x] VPS 배포 (git pull, 프론트엔드만 변경)
### Result
- 커밋 aca66dd
- VPS 배포 완료 (프론트엔드만 변경, PM2 재시작 불필요)
### Next (방향만)
- kie.ai 크레딧 충전 후 E2E 검증
- ao-produce 500 디버깅
### Files / Links
- productions-client.tsx (나레이션 섹션 + 자동 영상화 전환)

## 2026-03-06 (22차)
### Done
- [x] n8n Worker 콜백 STATUS_ORDER에 processing(2), generated(6), uploaded(10) 추가
- [x] uploaded 콜백 → completed로 매핑
- [x] 프롬프트 필수 조건 완전 제거 (모든 모드에서 선택사항)
- [x] 이미지 슬롯에서 영상 파일(mp4/mov) 업로드 가능
- [x] 영상 미리보기: autoPlay muted loop playsInline + 🎬 뱃지
- [x] VPS 배포 (백엔드 tsc + PM2 restart + 프론트엔드 git pull)
### Tried
- [x] 이전 production "농구장의 총잡이" 분석 → n8n Worker 성공(영상 생성됨) but 콜백 status 불일치로 웹앱 타임아웃
### Result
- 근본 원인: n8n Worker가 보내는 status(processing/generated/uploaded)가 웹앱 STATUS_ORDER에 없어서 모든 콜백 무시됨
- n8n Docker 설정 경로: /docker/n8n/docker-compose.yml (신규 발견)
- WEBAPP_CALLBACK_URL: 이미 설정됨 확인
### Next (방향만)
- 영상 제작 E2E 재시도 → completed 정상 확인
- kie.ai 크레딧 충전 후 이미지 생성 E2E
### Files / Links
- productions.ts (STATUS_ORDER + uploaded→completed 매핑)
- productions-client.tsx (프롬프트 선택사항 + 영상 슬롯 accept + 🎬 뱃지)

## 2026-03-06 (23차)
### Done
- [x] 미디어 슬롯 초기 1칸 → [+] 버튼으로 1칸씩 추가 (최대 20개)
- [x] imageSlots 초기값 [null,null,null] → [null] 변경 (리셋 포함 3곳)
- [x] maxImageSlots 항상 20 (모드 불문)
- [x] 이미지 다운로드: downloadViaProxy 백엔드 프록시 경유 (mixed content 해결)
- [x] 다운로드 중 로딩 스피너 표시 (downloadingIdx 상태)
- [x] images-client.tsx 다운로드도 프록시 경유로 통일
- [x] sessionStorage 작업 내용 자동 저장/복원 (DRAFT_KEY: ao_production_draft)
- [x] 영상 제작 시작 시 clearDraft() 호출
- [x] VPS 배포 (git pull, 프론트엔드만 변경)
### Result
- 커밋 fcf8f96
- VPS 배포 완료
- lib/media.ts에 downloadViaProxy 유틸 함수 추가
### Next (방향만)
- 영상 제작 E2E 재시도 (콜백 정상 수신 → completed 확인)
- kie.ai 크레딧 충전 후 이미지 생성 E2E
### Files / Links
- productions-client.tsx (슬롯 1칸 + sessionStorage + 다운로드 프록시)
- images-client.tsx (다운로드 프록시 + 로딩 스피너)
- lib/media.ts (downloadViaProxy 함수 추가)

## 2026-03-07
### Done
- [x] Phase 2: 입력 필드 정리 + payload 계약 맞추기
  - prompt_p1 필수 (UI `*` + 백엔드 400 검증 + 제작 버튼 비활성화)
  - duration 드롭다운 (30/60/90/120초)
  - engine_type 선택 (character_story/core_message/live_promo/meme/action_sports)
  - strict_mode 토글 (기본 false)
  - narration 3분리: narration_text + narration_style + narration_tone
  - narration_mode(auto/manual) 제거 → 텍스트 비우면 AI 자동
  - BGM/SFX: 체크박스 → 파일 업로드 방식 (업로드 없으면 무음)
  - SFX 업로드 칸 신규 (sfx_url → n8n payload)
  - topic/keywords/category: 접기 가능한 메타데이터 섹션
  - n8n Producer 입력값 검증 노드 업데이트 (top-level + activeVersion)
  - sessionStorage draft 새 필드 포함
  - backend duration 허용값 검증 [30,60,90,120]
- [x] TypeScript + quality-check PASS
### Result
- 3계층 (프론트→백엔드→n8n) payload 계약 통일
- enableBgm/enableSfx: 파일 업로드 여부로 자동 결정 (!!bgmUrl / !!sfxUrl)
### Next (방향만)
- VPS 배포 + n8n 워크플로우 업로드
- E2E 영상 제작 테스트
### Files / Links
- productions-client.tsx (Phase 2 UI 전면 수정)
- productions.ts (body 타입 + 검증 + webhook payload)
- ao_producer.json (입력값 검증 Code 노드)

## 2026-03-07 (2차)
### Done
- [x] 미디어 선택 옵션 정리: "새 이미지 생성"(generate) 옵션 UI에서 완전 제거
- [x] useMode 타입: 'direct' | 'generate' | 'analysis_only' → 'direct' | 'analysis_only'
- [x] SlotCard 라디오: 3개 → 2개 (직접 사용 / 분석만 반영)
- [x] "분석만 반영" 선택 시 Vision 분석 기반 프롬프트 자동 생성 + 수정 가능 입력칸 + 라벨 추가
- [x] 백엔드 body 타입은 하위호환 유지 (generate 허용)
- [x] TypeScript + quality-check PASS
### Result
- 프론트엔드만 변경 (백엔드/n8n 변경 없음)
- useMode에서 generate 완전 제거
### Next (방향만)
- VPS 배포 (프론트엔드만)
- E2E 영상 제작 테스트
### Files / Links
- productions-client.tsx (useMode generate 제거 + analysis_only UI 개선)
