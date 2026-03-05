# HANDOFF.md — 현재 상태/진행상황 (항상 전체 Overwrite)

> ✅ 이 파일은 "최신 스냅샷"이 목적이라 매번 전체 Overwrite가 정석입니다.
> (여기엔 최신 상태/Next/LastRun/Blockers만 유지)

🔎 INDEX: Current Status | Goal | Next Actions | Last Run Command | Result | Blockers | Known Issues | 변경 파일 | 다음 세션 메시지

---

## A) 상태 요약
- **현재 워크스페이스**: 웹앱
- **Current Status**: Phase 2 완료, Phase 3 부분 진행 (API만 완료, UI 미구현)
- **Goal**: Phase 3 잔여(프롬프트 에디터 UI, 캐릭터 관리 UI) 완성 → Phase 4 진입
- **Current Mental Model**: 4개 채널(루믹스/온카스터디/슬롯/스포츠) 영상 제작을 웹 UI로 트리거/모니터링/관리하는 플랫폼. Phase 2(제작 컨트롤) 완료, Phase 3(프롬프트+캐릭터) API만 완성, UI 미구현.

## B) 환경/의존성
- **서버**: VPS 76.13.182.180 (Hostinger KVM1, Malaysia)
- **Branch**: feature/web-app
- **Environment**: Production (Cloudflare Pages + VPS PM2)
- **Runtime/Versions**: TypeScript / Node.js (Next.js 14 + Fastify + Prisma)
  - 프론트엔드: Next.js 14 (App Router) + TypeScript + Tailwind CSS + shadcn/ui → Cloudflare Pages
  - 백엔드: Fastify + TypeScript + Prisma ORM → VPS PM2 (:3001)
  - DB: PostgreSQL (:5432)
  - 공유 타입: npm workspace `@n8n-web/shared`
  - n8n: self-hosted, queue-mode (:5678)
- **Required Secrets**: DATABASE_URL, JWT_SECRET, N8N_API_KEY, N8N_BASE_URL, N8N_WEBHOOK_BASE, CORS_ORIGIN, ADMIN_USERNAME, ADMIN_PASSWORD, PRODUCTION_TIMEOUT_MINUTES (모두 VPS `.env`에서 관리)

## C) 마지막 실행 기록 (필수)
- **Last Run Command**:
  ```bash
  # 백엔드 배포
  ssh root@n8n.srv1345711.hstgr.cloud \
    'cd /root/n8n-web && git pull origin feature/web-app && \
     npm run build:backend && pm2 restart n8n-web-backend'
  # 프론트엔드: git push → Cloudflare Pages 자동 빌드
  ```
- **Result**: 정상 동작 중 (Phase 2 완료 상태)
- **실행 위치**: VPS (백엔드) / Cloudflare Pages (프론트엔드)

## D) 완료/미완료

### Done ✅

**Phase 1: 기반**
- [x] 모노레포 구조 (npm workspaces)
- [x] Fastify + Prisma + PostgreSQL
- [x] JWT 인증 (단일 관리자)
- [x] 채널/워크플로우 CRUD
- [x] 대시보드 (통계, 최근 제작)
- [x] Cloudflare Pages + VPS 배포

**Phase 2: 제작 컨트롤**
- [x] 제작 트리거 (웹훅 → n8n) + 배치 제작
- [x] n8n 콜백 수신 (단계별 상태 업데이트, 역행 방지)
- [x] 실시간 제작 목록 (아코디언 + 자동 리패칭)
- [x] 제작 상세 페이지 (비디오 플레이어, 스텝퍼, 스크립트)
- [x] 정지/이어서 (paused + n8n stop/retry 연동)
- [x] 중단/재시도/다시 만들기 + n8n Retry API 연동
- [x] 보관/복원 (archived + previousStatus)
- [x] 삭제 (진행중 차단)
- [x] 스마트 타임아웃 (n8n 실행 상태 확인 후 판단, 기본 5분)
- [x] 능동 상태 동기화 (1분마다 n8n 실행 상태 API 확인)
- [x] 타임아웃 에러 시각 구분 (amber 색상 + 시계 아이콘)
- [x] 제작 상세 폴링 (진행중 3초, 완료/실패 시 중지)
- [x] 스텝퍼 워크플로우 유형 분리 (tts_based / video_based)
- [x] 미디어 프록시 (mixed content 해결) + 다운로드 파일명 보존
- [x] CORS PATCH/DELETE 수정

**보안**
- [x] CORS 도메인 제한 (프론트엔드 도메인만 허용, `*` 금지)
- [x] admin 기본 비밀번호 변경

**Phase 3: 프롬프트 + 캐릭터 (API만 완료)**
- [x] 프롬프트 CRUD API
- [x] 캐릭터 CRUD API

### In Progress 🔧
- [ ] Phase 3 UI 작업 대기 중

### Next Actions ➡️ (우선순위 1~3)
1. [ ] 프롬프트 에디터 UI (Monaco Editor) + n8n 배포 기능
2. [ ] 프롬프트 버전 이력 + diff 뷰 + 롤백
3. [ ] 캐릭터 카드 그리드 UI + 편집 폼

### 이후 로드맵
- **Phase 4**: YouTube Analytics API 연동, 미디어 라이브러리, 분석 대시보드
- **Phase 5**: 템플릿 시스템, 알림 연동 (Telegram/Slack), 스케줄링 UI, WebSocket 실시간 푸시

## E) Blockers / Issues
- **Blockers**: 없음
- **Known Issues**:
  1. Google Sheets OAuth 토큰 만료 — n8n에서 재인증 필요 (할머니+Mike 워크플로우)
  2. 이미지 URL 없음 — 이미지 생성 API가 간헐적으로 URL 미반환 (할머니+Mike #1223)
- **보안 주의**:
  1. CORS_ORIGIN은 반드시 `https://n8n-project-9lj.pages.dev`만 허용 (`*` 절대 금지)
  2. ADMIN_PASSWORD는 VPS `.env`에만 존재 (코드/문서에 평문 기록 금지)
  3. n8n 콜백(`/api/productions/callback`)은 인증 없음 — Nginx 내부 IP 제한 또는 시크릿 토큰 추가 권장
- **롤백 필요 시**: n8n 워크플로우는 백업 JSON Import, VPS 설정은 `.bak` 복사본, 컨테이너는 `docker-compose down && up -d`

## F) 변경 파일
```
packages/
├── frontend/          # Next.js → Cloudflare Pages
│   └── src/
│       ├── app/(dashboard)/   # 페이지 라우트
│       ├── components/        # UI 컴포넌트
│       ├── hooks/             # React Query 훅 (use-dashboard.ts)
│       ├── lib/               # api.ts, media.ts, utils.ts
│       └── types/
├── backend/           # Fastify → VPS PM2
│   ├── prisma/        # schema.prisma
│   └── src/
│       ├── routes/    # API 라우트
│       ├── jobs/      # 크론잡 (timeout-checker.ts)
│       ├── utils/     # n8n-client, prisma, logger
│       └── config.ts
└── shared/            # 프론트/백엔드 공유 타입
    └── src/index.ts
```

## G) 다음 세션 시작용 메시지 (복붙)
> n8n-web 프로젝트 (YouTube 영상 자동 제작 관리 플랫폼). Phase 2(제작 컨트롤) 완료, Phase 3 API 완성 상태. 다음 작업: 프롬프트 에디터 UI(Monaco) + 캐릭터 관리 UI 구현. 브랜치: feature/web-app. 워크스페이스: 웹앱.

---

## 참조: 핵심 패턴

### 서버/클라이언트 분리 (Cloudflare Pages 필수)
- `page.tsx`: Server Component (`export const runtime = 'edge'`)
- `*-client.tsx`: Client Component (`'use client'`)
- **절대 같은 파일에 `'use client'`와 `runtime = 'edge'`를 넣지 말 것**

### API 클라이언트 (lib/api.ts)
- body 없는 요청(GET, DELETE)에 Content-Type 헤더 미설정 (Fastify 파싱 에러 방지)
- 401 시 자동 로그아웃 + /login 리다이렉트

### 미디어 프록시 (lib/media.ts)
- MinIO(HTTP) → 백엔드 프록시(HTTPS) → 프론트엔드 (mixed content 방지)
- `proxyMediaUrl()`: HTTP URL을 `/api/media/proxy?url=...`로 변환
- 허용 호스트(76.13.182.180)만 프록시, Range 헤더 지원

### DB 스키마: ProductionStatus
```
pending → started → script_ready → tts_ready → images_ready →
videos_ready → rendering → uploading → completed
                                                  ↘ failed (언제든)
                                                  ↘ paused (사용자)
                                                  ↘ archived (보관)
```

### n8n 연동 패턴
| 패턴 | 방식 |
|------|------|
| 제작 트리거 | 백엔드 → `N8N_WEBHOOK_BASE/{webhookPath}` POST |
| 상태 콜백 | n8n → `백엔드/api/productions/callback` POST (인증 없음, executionId 포함) |
| 실행 중단 | 백엔드 → n8n `POST /api/v1/executions/{id}/stop` |
| 실행 재시도 | 백엔드 → n8n `POST /api/v1/executions/{id}/retry` |
| 워크플로우 조회 | 백엔드 → n8n REST API GET |
| 실행 이력 | 백엔드 → n8n `/api/v1/executions` GET |

### 콜백 본문 형식
```json
{
  "productionId": "uuid",
  "status": "script_ready|tts_ready|images_ready|videos_ready|rendering|completed|failed",
  "title": "영상 제목",
  "assets": { "videoUrl": "...", "thumbnailUrl": "...", "script": "..." },
  "errorMessage": "에러 시",
  "executionId": "n8n 실행 ID (재시도용)"
}
```

### 워크플로우 목록 (DB)
| 이름 | 타입 | webhook_path | n8n ID | stepper |
|------|------|------|------|------|
| [온카 스터디] 설명형 숏츠 v16 | shortform | onca-shortform-v16 | x6xTzHJ9WbUc94ec | tts_based |
| 온카스터디 스토리짤 v7 (할머니+Mike) | story_shorts | story-grandma-mike | jRT8nmDr34S96I1b | video_based |
| Jay+Mike 스토리형 v84 | story_shorts | story-jay-mike | jSEDYrkFcWUzJ8Et | video_based |
| 흑형스포츠 v84 | story_shorts | story-sports | ZP6rY0wz70AIJuPU | video_based |

### 배포 명령어
```bash
# 프론트엔드: git push → Cloudflare Pages 자동 빌드

# 백엔드 배포:
ssh root@n8n.srv1345711.hstgr.cloud \
  'cd /root/n8n-web && git pull origin feature/web-app && \
   npm run build:backend && pm2 restart n8n-web-backend'

# Prisma 스키마 변경 시:
ssh root@n8n.srv1345711.hstgr.cloud \
  'cd /root/n8n-web/packages/backend && npx prisma generate && \
   cd /root/n8n-web && npm run build:backend && pm2 restart n8n-web-backend'

# DB enum 추가 시:
ssh root@n8n.srv1345711.hstgr.cloud \
  "sudo -u postgres psql -d n8n_web -c \"ALTER TYPE \\\"ProductionStatus\\\" ADD VALUE IF NOT EXISTS 'new_value';\""

# DB 직접 접근:
ssh root@n8n.srv1345711.hstgr.cloud "sudo -u postgres psql -d n8n_web"
```
