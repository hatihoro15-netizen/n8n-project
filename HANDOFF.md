# HANDOFF - 온카 숏폼 v16 워크플로우

> 마지막 업데이트: 2026-03-04

## 현재 상태

- **브랜치:** `feature/onca-shortform-v16`
- **워크플로우 ID:** `x6xTzHJ9WbUc94ec`
- **n8n 서버:** `https://n8n.srv1345711.hstgr.cloud`
- **워크플로우 상태:** Active (42 노드)
- **최신 커밋:** `609b7ff` E2E 테스트 실패 분석 기록
- **웹앱 배포:** 2026-03-04 완료 (executionId 매핑 → n8nExecutionId 정상 저장 확인)

## 최근 작업 요약 (2026-03-02~03)

### 1. 웹앱 연동: Webhook + 콜백 시스템 (`f1a620a`)
- Webhook POST `/onca-shortform-v16` 추가 (responseMode: onReceived)
- 성공 콜백: 상태 업데이트 → 콜백 데이터 준비 → 콜백 필요?(IF) → 성공 콜백
- 실패 콜백: NCA 영상 제작 에러출력 → 실패 콜백 준비 → 실패 콜백
- 수동 실행 시 콜백 스킵 (skipCallback 분기)

### 2. 중간 단계 콜백 (`80b9965`)
- 4개 병렬 분기로 메인 흐름에 지연 없음
- `script_ready` (콘텐츠 파싱 후)
- `tts_ready` (TTS 결과 처리 후)
- `images_ready` (이미지 URL 추출 후)
- `rendering` (NCA 데이터 준비 후)
- HTTP 노드에 `onError: continueRegularOutput` (실패해도 메인 흐름 무관)

### 3. v3 종합 패치 머지 (`d3c58d1`)
- 프롬프트 앵커 시스템 + 콘텐츠 검증 강화 + 사투리 + 밈 mood 매칭
- 패치 파일(20노드)에서 변경된 5개 노드 parameters만 34노드 파일에 머지
- 머지된 노드: 콘텐츠 파싱, 프롬프트 생성, AI 주제 생성, 주제 파싱, 카테고리 결정

### 4. 에러 핸들링 강화 (`f6c9608`)
- 서버 38노드 버전 동기화 (n8n 에디터에서 추가된 에러 준비 4개 포함)
- 콘텐츠 파싱 / 주제 파싱에 `onError: continueErrorOutput` 추가
- 전체 에러 경로 7개 → 모두 실패 콜백으로 연결

### 5. 콜백 executionId 추가 (`fff8f3b`)
- 모든 콜백 HTTP Request 노드(6개) body에 `executionId: $execution.id` 추가
- 대상: 성공 콜백, 실패 콜백, 스크립트 콜백, TTS 콜백, 이미지 콜백, 렌더링 콜백
- 웹앱에서 n8n 실행 ID로 디버깅 가능

### 6. 웹앱 executionId 매핑 배포 (2026-03-04)
- **문제:** 웹앱 DB의 모든 production에서 `n8n_execution_id`가 NULL
- **원인:** n8n은 `executionId`를 콜백 body에 이미 포함 중이었으나, 웹앱 콜백 API의 executionId 매핑 코드(`8d8769e`)가 마지막 n8n 실행 이후에 커밋됨
- **해결:** 코드 변경 없이 웹앱 백엔드 VPS 재배포 (`deploy/deploy.sh`)
- **배포 확인:** PM2 `n8n-web-backend` online (PID: 303072)
- **검증 완료:** 실행 #1280에서 `n8nExecutionId: "1280"` 정상 저장 확인

### 7. 주제 파싱 금지어 조기 검증 추가 (2026-03-04)
- **문제:** 실행 #1280에서 "콘텐츠 파싱 실패" 5초 에러
- **원인:** AI 주제 생성이 카테고리 4(방송존)인데 "200만원 증발된 억울함" 주제 생성 → 콘텐츠 파싱 TOPIC_CONFLICT에서 "증발" 금지어 감지
- **근본 원인:** 주제 파싱에 금지어 검증 없이 통과 → 불필요한 AI 콘텐츠 생성 호출
- **수정:** 주제 파싱 노드에 2단계 조기 검증 추가
  - NEGATIVE_BLOCKLIST: 비-먹튀 카테고리(2~5)에서 부정 키워드 금지 (topic 텍스트 대상)
  - TOPIC_CONFLICT: subtopic-topic 충돌 검증 (콘텐츠 파싱과 동일 규칙)
- **효과:** AI 콘텐츠 생성 호출 전에 차단 → Gemini API 비용 절감 + 빠른 실패
- **서버 반영:** n8n API PUT 업로드 완료 (top-level + activeVersion 양쪽)

### 8. E2E 테스트 2건 연속 실패 분석 (2026-03-04)
- **실행 #1286:** topic 미입력 → AI가 "역대급 먹튀 사건" 생성 → 주제 파싱 NEGATIVE_BLOCKLIST "먹튀" 차단 (2초)
- **실행 #1287:** topic "안녕" 입력 → AI가 "역대급 먹튀썰" 생성 → 동일 차단 (2초)
- **조기 검증 효과 확인:** 콘텐츠 파싱까지 안 가고 주제 파싱에서 차단 → AI 콘텐츠 생성 비용 절감
- **근본 원인:**
  1. AI 주제 생성(Gemini)이 카테고리 4(방송존)인데 계속 먹튀/사기 주제 생성 (프롬프트 무시)
  2. webhook의 topic 필드("안녕")가 AI 주제 생성에 전달/반영되지 않음
  3. 3연속(#1280~#1287) 카테고리 4 고정 → 카운터 순환 확인 필요
- **미해결:** AI 프롬프트 강화 또는 리트라이 로직 검토 필요

### 9. 실패 시 카운터 고정 문제 수정 (2026-03-04)
- **문제:** 카운터 = Google Sheets 행 수인데, 실패 시 시트 기록이 안 되어 같은 카테고리 무한 반복
- **원인:** 에러 경로 7개가 모두 시트 기록 없이 실패 콜백으로 직통
- **수정:**
  - "실패 시트 기록" Google Sheets append 노드 1개 추가 (onError: continueRegularOutput)
  - 에러 준비 노드 7개에 시트용 컬럼 추가 (Status: "실패", category, subtopic, generatedAt, Subject)
  - 에러 준비 → [실패 콜백, 실패 시트 기록] 병렬 연결
- **효과:** 실패해도 시트에 행 추가 → 카운터 진행 → 다음 카테고리로 넘어감
- **서버 반영:** n8n API PUT 업로드 완료 (41 노드)

### 10. Webhook vs 수동 실행 차이 분석 (2026-03-04)
- **실행 #1292 (webhook):** AI 주제 생성에서 Gemini rate limit 에러 → AI 주제 에러 준비 → 실패 콜백 + 실패 시트 기록
- **실행 #1285 (수동):** AI 주제 생성 정상 (980ms) → 주제 파싱 → 프롬프트 생성까지 진행
- **에러 원인:** Gemini API rate limit (`"The service is receiving too many requests from you"`)
- **webhook만 실패 이유:** 웹앱 E2E 테스트로 짧은 간격(수 초) 연속 호출 → rate limit 초과
- **수동 정상 이유:** 실행 간 간격 충분하여 rate limit 미초과
- **부수 이슈:** 에러 준비 노드가 `input.error`가 문자열일 때 메시지 추출 실패 → "알 수 없는 에러"로 폴백
  - 수정 필요: `typeof input.error === 'string' ? input.error : (input.error?.message || ...)` 처리
- **카운터:** 실패 시트 기록 정상 작동 확인 (2524ms)

### 11. AI 주제 생성 프롬프트 강화 + 리트라이 로직 추가 (2026-03-04)
- **문제:** Gemini가 카테고리/소재와 무관한 주제를 계속 생성 (예: 카테고리 4에서 "먹튀" 주제)
- **수정 1: 프롬프트 강화**
  - subtopic(소재) 필드를 프롬프트에 주입: `소재: '{{ $json.subtopic }}'`
  - 해당 카테고리 톤만 표시 (n8n 삼항 표현식 사용)
  - 카테고리별 금지어 조건부 표시: `{{ $json.category != 1 ? '...' : '' }}`
  - 기존: 5개 카테고리 전부 나열 → 변경: 해당 카테고리만 + 소재 범위 제한
- **수정 2: 리트라이 판단 노드 추가**
  - `리트라이 판단` Code 노드 (n8n-nodes-base.code, typeVersion 2)
  - 주제 파싱 검증 실패 시 최대 2회 재시도 후 에러 경로
  - output[0] (retry) → AI 주제 생성 (루프백)
  - output[1] (give up) → 주제 파싱 에러 준비
  - `$('카테고리 결정').first().json.topicRetryCount`로 재시도 횟수 추적
- **연결 변경:**
  - 기존: 주제 파싱 error → 주제 파싱 에러 준비
  - 변경: 주제 파싱 error → 리트라이 판단 → [AI 주제 생성 / 주제 파싱 에러 준비]
- **테스트 (#1310):** category 1, subtopic "먹튀 제보와 검증 과정" 전달 확인
  - Gemini가 "스포츠 승무패 예측" 생성 (여전히 무관한 주제)
  - 주제 파싱 통과 (category 1은 금지어 제외 대상)
  - AI 콘텐츠 생성에서 에러 → 실패 경로 진행
- **서버 반영:** n8n API PUT 업로드 완료 (42 노드)
- **미해결:** Gemini가 프롬프트 강화 후에도 소재와 무관한 주제 생성 (모델 한계)

## 에러 핸들링 커버리지

| 에러 발생 노드 | 에러 준비 노드 | → 실패 콜백 |
|---|---|---|
| AI 주제 생성 | AI 주제 에러 준비 | → 실패 콜백 |
| 주제 파싱 | 주제 파싱 에러 준비 | → 실패 콜백 |
| AI 콘텐츠 생성 | AI 콘텐츠 에러 준비 | → 실패 콜백 |
| 콘텐츠 파싱 | 콘텐츠 파싱 에러 준비 | → 실패 콜백 |
| TTS 요청 | TTS 에러 준비 | → 실패 콜백 |
| 이미지 검색 | 이미지 검색 에러 준비 | → 실패 콜백 |
| NCA 영상 제작 | 실패 콜백 준비 | → 실패 콜백 |

## 콜백 API

- **URL:** `POST https://api-n8n.xn--9g4bn4fm2bl2mb9f.com/api/productions/callback`
- **상태 값:** `script_ready` → `tts_ready` → `images_ready` → `rendering` → `completed` / `failed`
- **공통 필드:** `productionId`, `status`, `executionId` (n8n 실행 ID)
- **성공 추가 필드:** `title`, `videoUrl`
- **실패 추가 필드:** `errorMessage`
- **Prisma enum:** `ProductionStatus`에 모든 값 정의됨
- **주의:** 콜백 엔드포인트에 status 검증 로직 없음 (Prisma enum이 방어)

## 워크플로우 전체 흐름

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

## n8n API 참고

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

## 알려진 이슈

- Gemini API rate limit 시 AI 주제 생성 에러 발생 (연속 webhook 실행 시 주의, #1292에서 확인됨)
- 에러 준비 노드의 에러 메시지 추출이 `input.error` 문자열 타입 미처리 → "알 수 없는 에러"로 폴백
- 콜백 API에 status 검증 로직 없음 (추가 권장)
- 가짜 productionId로 테스트 시 콜백 API에서 404/500 발생 (정상 동작)
