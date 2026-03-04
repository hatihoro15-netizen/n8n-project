# n8n-web 프로젝트 핸드오프 문서

## 프로젝트 개요

n8n 워크플로우 기반 YouTube 영상 자동 제작 관리 플랫폼.
4개 채널(루믹스, 온카스터디, 슬롯, 스포츠)의 영상 제작을 웹 UI로 트리거/모니터링/관리.

## 기술 스택

| 영역 | 기술 |
|------|------|
| 프론트엔드 | Next.js 14 (App Router) + TypeScript + Tailwind CSS + shadcn/ui |
| 백엔드 | Fastify + TypeScript + Prisma ORM |
| DB | PostgreSQL |
| 공유 타입 | npm workspace `@n8n-web/shared` |
| 프론트 배포 | Cloudflare Pages (자동 빌드) |
| 백엔드 배포 | Hostinger VPS + PM2 |

## 배포 아키텍처

```
Cloudflare Pages (프론트엔드)
    │ HTTPS
    ▼
Hostinger VPS (n8n.srv1345711.hstgr.cloud)
    ├── Nginx (리버스 프록시)
    │   ├── api.도메인 → :3001 (백엔드)
    │   └── n8n.도메인 → :5678 (n8n)
    ├── Fastify 백엔드 (:3001) ←→ n8n (:5678) [localhost 통신]
    └── PostgreSQL (:5432)
```

## 배포 명령어

```bash
# 프론트엔드: git push하면 Cloudflare Pages 자동 빌드

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

# n8n API 호출:
ssh root@n8n.srv1345711.hstgr.cloud \
  'API_KEY=$(grep N8N_API_KEY /root/n8n-web/packages/backend/.env | cut -d= -f2 | tr -d "\""); \
   curl -s "https://n8n.srv1345711.hstgr.cloud/api/v1/executions?limit=5" -H "X-N8N-API-KEY: $API_KEY"'
```

## 프로젝트 구조

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

## 핵심 패턴

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
- 백엔드: 허용 호스트(76.13.182.180)만 프록시, Range 헤더 지원

## DB 스키마 핵심

### ProductionStatus enum
```
pending → started → script_ready → tts_ready → images_ready →
videos_ready → rendering → uploading → completed
                                                  ↘ failed (언제든)
                                                  ↘ paused (사용자)
                                                  ↘ archived (보관)
```

### Production 테이블 주요 필드
- `previousStatus`: 보관 전 원래 상태 (복원 시 사용)
- `assets`: JSON (videoUrl, thumbnailUrl, script 등)
- `stepperType`: workflow에서 상속 (`tts_based` | `video_based`)

## 구현 완료 기능

### Phase 1: 기반
- [x] 모노레포 구조 (npm workspaces)
- [x] Fastify + Prisma + PostgreSQL
- [x] JWT 인증 (단일 관리자)
- [x] 채널/워크플로우 CRUD
- [x] 대시보드 (통계, 최근 제작)
- [x] Cloudflare Pages + VPS 배포

### Phase 2: 제작 컨트롤
- [x] 제작 트리거 (웹훅 → n8n)
- [x] 배치 제작
- [x] n8n 콜백 수신 (중간 단계별 상태 업데이트)
- [x] 콜백 역행 방지 (STATUS_ORDER)
- [x] 실시간 제작 목록 (아코디언 + 자동 리패칭)
- [x] 제작 상세 페이지 (비디오 플레이어, 스텝퍼, 스크립트)
- [x] 정지/이어서 (paused 상태 + n8n 실행 stop/retry 연동)
- [x] 중단/재시도/다시 만들기
- [x] 제작 보관/복원 (archived + previousStatus)
- [x] 제작 삭제 (진행중 차단)
- [x] 타임아웃 자동 실패 (크론잡, 기본 5분, 환경변수 조절)
- [x] 스텝퍼 워크플로우 유형 분리 (tts_based / video_based)
- [x] 스마트 타임아웃 (n8n 실행 상태 확인 후 판단 — running이면 연장, error/stopped면 실패, 콜백 미수신 감지)
- [x] 능동 상태 동기화 (1분마다 진행중 건의 n8n 실행 상태를 API로 확인, 즉시 반영)
- [x] 타임아웃 에러 시각 구분 (amber 색상 + 시계 아이콘)
- [x] n8n 실행 Retry API 연동 (에러 지점부터 재시도)
- [x] 제작 상세 폴링 (진행중 3초 간격, 완료/실패 시 중지)

### Phase 2 부가
- [x] 미디어 프록시 (mixed content 해결)
- [x] 다운로드 파일명 보존
- [x] CORS PATCH 메서드 지원
- [x] DELETE 빈 body Content-Type 수정

### 보안
- [x] CORS 도메인 제한 (`CORS_ORIGIN` → 프론트엔드 도메인만 허용, `*` 금지)
- [x] admin 기본 비밀번호 변경 (changeme → 강력한 랜덤 비밀번호)

### Phase 3: 프롬프트 + 캐릭터 (부분)
- [x] 프롬프트 CRUD API
- [x] 캐릭터 CRUD API
- [ ] 프롬프트 에디터 UI (Monaco)
- [ ] 프롬프트 n8n 배포 기능
- [ ] 버전 이력 + diff
- [ ] 캐릭터 관리 UI

## 워크플로우 목록 (DB)

| 이름 | 타입 | webhook_path | n8n ID | stepper |
|------|------|------|------|------|
| [온카 스터디] 설명형 숏츠 v16 | shortform | onca-shortform-v16 | x6xTzHJ9WbUc94ec | tts_based |
| 온카스터디 스토리짤 v7 (할머니+Mike) | story_shorts | story-grandma-mike | jRT8nmDr34S96I1b | video_based |
| Jay+Mike 스토리형 v84 | story_shorts | story-jay-mike | jSEDYrkFcWUzJ8Et | video_based |
| 흑형스포츠 v84 | story_shorts | story-sports | ZP6rY0wz70AIJuPU | video_based |

## 환경변수 (.env)

```bash
# packages/backend/.env
DATABASE_URL="postgresql://..."
JWT_SECRET="..."
N8N_BASE_URL="https://n8n.srv1345711.hstgr.cloud"
N8N_API_KEY="eyJhbGci..."
N8N_WEBHOOK_BASE="https://n8n.srv1345711.hstgr.cloud/webhook"
CORS_ORIGIN="https://n8n-project-9lj.pages.dev"  # 프론트 도메인만 허용 (절대 * 금지)
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="..."  # VPS .env에서 직접 확인 (절대 코드에 하드코딩 금지)
PRODUCTION_TIMEOUT_MINUTES=5  # 스마트 타임아웃 적용 (n8n 실행 중이면 자동 연장)
```

## n8n 연동 패턴

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

## 보안 주의사항

1. **CORS**: `CORS_ORIGIN`은 반드시 프론트엔드 도메인(`https://n8n-project-9lj.pages.dev`)만 허용. `*` 절대 금지.
2. **비밀번호**: `ADMIN_PASSWORD`는 VPS `.env`에만 존재. 코드/문서에 평문 기록 금지.
3. **n8n 콜백**: `/api/productions/callback`은 인증 없음 — VPS Nginx에서 내부 IP만 허용하거나 별도 시크릿 토큰 추가 권장.

## 알려진 이슈

1. **Google Sheets OAuth 토큰 만료** — n8n에서 재인증 필요 (할머니+Mike 워크플로우)
2. **이미지 URL 없음** — 이미지 생성 API가 간헐적으로 URL 미반환 (할머니+Mike #1223)
3. ~~**타임아웃 현재 30분**~~ — 5분 원복 완료 + 스마트 타임아웃 적용 (n8n 실행 중이면 자동 연장)

## 다음 작업 (미구현)

### Phase 3 잔여
- 프롬프트 에디터 UI (Monaco Editor)
- 프롬프트 n8n 배포 ("배포" 버튼 → n8n API PUT으로 워크플로우 노드 업데이트)
- 프롬프트 버전 이력 + diff 뷰 + 롤백
- 캐릭터 카드 그리드 UI + 편집 폼

### Phase 4: 미디어 + 분석
- YouTube Analytics API 연동
- 미디어 라이브러리 (생성 이미지/영상 브라우징)
- 분석 대시보드 (차트, 트렌드)

### Phase 5: 확장
- 템플릿 시스템
- 알림 연동 (Telegram/Slack)
- 스케줄링 UI
- WebSocket 실시간 푸시 (현재 폴링)
