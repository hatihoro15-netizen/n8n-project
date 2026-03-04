# HANDOFF.md — 현재 상태/진행상황 (항상 전체 Overwrite)

## A) 상태 요약
- **현재 프로젝트**: 온카스터디
- **Current Status**: AI 주제 생성 프롬프트 강화 + 리트라이 로직 추가 완료 (42노드)
- **Goal**: 숏폼 자동 생성 워크플로우 v16 안정화
- **Current Mental Model**: Gemini가 프롬프트 강화 후에도 소재와 무관한 주제를 생성하는 문제가 남아 있음. 에러 핸들링/콜백/카운터 시스템은 안정화됨.

## B) 환경/의존성
- **서버**: VPS 76.13.182.180 (Hostinger KVM1, Malaysia)
- **Branch**: `feature/onca-shortform-v16`
- **Environment**: Production (n8n self-hosted, queue-mode)
- **n8n URL**: `https://n8n.srv1345711.hstgr.cloud`
- **워크플로우 ID**: `x6xTzHJ9WbUc94ec`
- **Runtime/Versions**: Node.js (n8n), Python 3.11 (백엔드), Gemini (AI), ElevenLabs (TTS), Kie.ai/fal.ai (영상), NCA Toolkit + FFmpeg (합성), MinIO (스토리지)
- **Required Secrets**: N8N_API_KEY (값 기재 금지)

## C) 마지막 실행 기록 (필수)
- **Last Run Command**: Webhook POST `/onca-shortform-v16` (웹앱 E2E 테스트)
- **Result**: 실행 #1310 — category 1, subtopic "먹튀 제보와 검증 과정" → Gemini가 "스포츠 승무패 예측" 생성 (소재 무관) → 주제 파싱 통과 (category 1은 금지어 제외) → AI 콘텐츠 생성에서 에러 → 실패 경로 진행
- **실행 위치**: VPS (n8n 서버)

## D) 완료/미완료

### Done ✅
- [x] Webhook + 콜백 시스템 구축 (`f1a620a`)
  - Webhook POST `/onca-shortform-v16` (responseMode: onReceived)
  - 성공/실패 콜백, 수동 실행 시 콜백 스킵 (skipCallback 분기)
- [x] 중간 단계 콜백 4개 (`80b9965`)
  - `script_ready`, `tts_ready`, `images_ready`, `rendering` (병렬 분기, 실패해도 메인 흐름 무관)
- [x] v3 종합 패치 머지 (`d3c58d1`)
  - 프롬프트 앵커 시스템 + 콘텐츠 검증 강화 + 사투리 + 밈 mood 매칭
  - 머지 노드: 콘텐츠 파싱, 프롬프트 생성, AI 주제 생성, 주제 파싱, 카테고리 결정
- [x] 에러 핸들링 7개 경로 완비 (`f6c9608`)
  - AI 주제/주제 파싱/AI 콘텐츠/콘텐츠 파싱/TTS/이미지 검색/NCA 영상 제작
  - 콘텐츠 파싱/주제 파싱에 `onError: continueErrorOutput` 추가
- [x] 콜백 executionId 추가 (`fff8f3b`)
  - 6개 콜백 HTTP Request 노드 body에 `executionId: $execution.id` 추가
- [x] 웹앱 executionId 매핑 배포 (2026-03-04)
  - 웹앱 백엔드 VPS 재배포 → PM2 `n8n-web-backend` online (PID: 303072)
  - 실행 #1280에서 `n8nExecutionId: "1280"` 정상 저장 확인
- [x] 주제 파싱 금지어 조기 검증 추가 (2026-03-04)
  - NEGATIVE_BLOCKLIST + TOPIC_CONFLICT 2단계 조기 검증
  - AI 콘텐츠 생성 전 차단 → Gemini API 비용 절감 + 빠른 실패
- [x] 실패 시 카운터 고정 문제 수정 (2026-03-04)
  - "실패 시트 기록" Google Sheets append 노드 추가
  - 에러 준비 7개에 시트용 컬럼 추가 → 에러 경로에서 병렬 시트 기록
  - 실패해도 카운터 진행 → 다음 카테고리로 넘어감
- [x] AI 주제 생성 프롬프트 강화 + 리트라이 판단 노드 추가 (2026-03-04)
  - subtopic 주입, 해당 카테고리 톤만 표시, 카테고리별 금지어 조건부 표시
  - 리트라이 판단 Code 노드: 최대 2회 재시도 후 에러 경로

### In Progress 🔧
- [ ] Gemini 주제 생성 품질 개선 — 프롬프트 강화 후에도 소재와 무관한 주제 생성 (모델 한계)
- [ ] 에러 준비 노드 `input.error` 문자열 타입 미처리 → "알 수 없는 에러" 폴백 문제

### Next Actions ➡️ (우선순위 1~3)
1. [ ] Gemini 주제 생성 개선: 프롬프트 추가 강화 또는 다른 모델 검토
2. [ ] 에러 준비 노드 에러 메시지 추출 개선: `typeof input.error === 'string' ? input.error : (input.error?.message || ...)` 처리
3. [ ] 콜백 API에 status 검증 로직 추가 (현재 Prisma enum만 방어)

## E) Blockers / Issues
- **Blockers**: Gemini가 카테고리/소재와 무관한 주제를 반복 생성 (프롬프트 강화로도 미해결, 모델 한계 가능성)
- **Known Issues**:
  - Gemini API rate limit 시 AI 주제 생성 에러 (연속 webhook 실행 시, #1292에서 확인)
  - 에러 준비 노드의 `input.error` 문자열 타입 미처리 → "알 수 없는 에러" 폴백
  - 콜백 API에 status 검증 로직 없음 (Prisma enum만 방어)
  - 가짜 productionId로 테스트 시 콜백 API에서 404/500 발생 (정상 동작)
  - Webhook vs 수동 실행: 웹앱 E2E 연속 호출 시 rate limit 초과 가능 (#1292)
- **롤백 필요 시**: n8n API로 백업 JSON Import, 워크플로우 ID `x6xTzHJ9WbUc94ec`

## F) 변경 파일
- `onca-shortform-v16.json` — 메인 워크플로우 (42노드)
- 웹앱 백엔드: 콜백 API executionId 매핑 (코드 변경 없이 재배포)

## G) 참고 정보

### 에러 핸들링 커버리지

| 에러 발생 노드 | 에러 준비 노드 | → 실패 콜백 |
|---|---|---|
| AI 주제 생성 | AI 주제 에러 준비 | → 실패 콜백 |
| 주제 파싱 | 주제 파싱 에러 준비 | → 실패 콜백 |
| AI 콘텐츠 생성 | AI 콘텐츠 에러 준비 | → 실패 콜백 |
| 콘텐츠 파싱 | 콘텐츠 파싱 에러 준비 | → 실패 콜백 |
| TTS 요청 | TTS 에러 준비 | → 실패 콜백 |
| 이미지 검색 | 이미지 검색 에러 준비 | → 실패 콜백 |
| NCA 영상 제작 | 실패 콜백 준비 | → 실패 콜백 |

### 콜백 API

- **URL**: `POST https://api-n8n.xn--9g4bn4fm2bl2mb9f.com/api/productions/callback`
- **상태 값**: `script_ready` → `tts_ready` → `images_ready` → `rendering` → `completed` / `failed`
- **공통 필드**: `productionId`, `status`, `executionId` (n8n 실행 ID)
- **성공 추가 필드**: `title`, `videoUrl`
- **실패 추가 필드**: `errorMessage`
- **Prisma enum**: `ProductionStatus`에 모든 값 정의됨

### 워크플로우 전체 흐름

```
[Webhook POST]  ─┐
                  ├→ 카운터 읽기 → 카테고리 결정 → AI 주제 생성 → 주제 파싱
[수동 실행]     ─┘                                 ↑    │(에러)       │(에러)
                                                   │    ↓             ↓
                                                   │  AI주제에러준비  리트라이 판단
                                                   │    ↓            ↙(retry) ↘(give up)
                                                   └────────────    주제파싱에러준비
                                                     (최대2회)           ↓
                                                                     실패 콜백

→ 프롬프트 생성 → AI 콘텐츠 생성 → 콘텐츠 파싱 → 시트 기록 → TTS/이미지 병렬
                       │(에러)         │(에러)         │(콜백)
                       ↓               ↓               ↓
                 AI콘텐츠에러준비  콘텐츠파싱에러준비  스크립트콜백
                       ↓               ↓
                  ┌─ 실패 콜백    ┌─ 실패 콜백
                  └─ 실패시트기록 └─ 실패시트기록   ※ 모든 에러 경로에서 병렬 시트 기록

→ Merge → Aggregate → NCA 데이터 준비 → NCA 영상 제작 → 결과 처리 → 상태 업데이트
                            │(콜백)           │(에러)                      │
                            ↓                 ↓                            ↓
                        렌더링콜백       실패콜백준비              콜백데이터준비
                                              ↓                            ↓
                                           실패콜백                   콜백필요?
                                                                     ↙      ↘
                                                                성공콜백    (끝)
```

### n8n API 참고

```bash
# 워크플로우 조회
curl -s "https://n8n.srv1345711.hstgr.cloud/api/v1/workflows/x6xTzHJ9WbUc94ec" \
  -H "X-N8N-API-KEY: $N8N_API_KEY"

# 워크플로우 업로드 (pinData/staticData 제외)
curl -X PUT ".../api/v1/workflows/x6xTzHJ9WbUc94ec" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d @upload.json

# 활성화
curl -X POST ".../api/v1/workflows/x6xTzHJ9WbUc94ec/activate" \
  -H "X-N8N-API-KEY: $N8N_API_KEY"

# 최근 실행 조회
curl -s ".../api/v1/executions?workflowId=x6xTzHJ9WbUc94ec&limit=5" \
  -H "X-N8N-API-KEY: $N8N_API_KEY"

# 실행 상세 (데이터 포함)
curl -s ".../api/v1/executions/{id}?includeData=true" \
  -H "X-N8N-API-KEY: $N8N_API_KEY"
```

## H) 다음 세션 시작용 메시지 (복붙)
> 온카 숏폼 v16 워크플로우 (42노드). 에러 핸들링/콜백/카운터 시스템 안정화 완료. Gemini 주제 생성 품질 문제(소재 무관 주제 반복)가 미해결 blocker. 에러 준비 노드 input.error 문자열 처리도 미수정.
