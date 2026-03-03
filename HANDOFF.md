# 세션 인수인계 (HANDOFF)

## 마지막 업데이트: 2026-03-03

## 현재 상태
- **브랜치**: `feature/v84-prompt-update`
- **3개 워크플로우 운영 중** (n8n 서버 active)

| 워크플로우 | n8n ID | 노드수 | 상태 |
|---|---|---|---|
| Jay+Mike v84 | jSEDYrkFcWUzJ8Et | 77 | active |
| 할머니+Mike v84 | jRT8nmDr34S96I1b | 76 | active |
| 흑형스포츠 v84 | ZP6rY0wz70AIJuPU | 74 | active |

## 오늘 적용된 변경사항 (커밋 순서)

### 1. 콜백 productionId 수정 (`78c60da`)
- 33개 콜백 노드의 productionId 추출 로직 수정
- Webhook 우선 → Execute Workflow Trigger 폴백, 각각 독립 try-catch

### 2. v86.4 패치 (`593d791`)
- 부분일치 금지어 규칙 추가 (AI 프롬프트)
- 프레임 추출 타이밍 -ss 7.0 → 7.8
- 콘텐츠 파싱 fullDialogue → dialogue_turns 기반
- NCA 데이터 준비: cleanDialogueTags + videoUrl 없으면 throw
- 영상N 실패체크: 1회 재생성 후 실패 시 throw (IF 노드 6개 추가)
- 대상: Jay+Mike, 할머니+Mike만

### 3. v86.6 Veo3 오디오 안전필터 대응 (`f33f9c0`, `8e29950`)
- 13-A: AI 프롬프트에 오디오 민감 표현 금지 섹션 추가 + 예시 순화
- 13-B: 영상1/2/3 준비에 safeReplaceAudio 코드 치환 삽입
- 13-C: 영상1/2/3 실패체크에 errorCode 400 판정 추가
- 대상: 3개 워크플로우 전부

### 4. 영상 준비 재시도 버그 수정 (`9cb99dd`)
- 영상1 준비: 재시도 시 `$('이미지 URL 추출')` 폴백 추가
- 영상1/2/3 준비: onError → continueErrorOutput + 에러 준비 연결
- 대상: 3개 워크플로우 전부

### 5. 중간 콜백 병렬→직렬 변경 (`60021e7`)
- n8n wait/polling 노드에서 병렬 side branch가 실행되지 않는 문제 대응
- 스크립트 콜백: `콘텐츠 파싱 → 준비 → 콜백 → 시트 기록`
- 이미지 콜백: `이미지 완료체크 → 준비 → 콜백 → 영상1 준비`
- 렌더링 콜백: `NCA 데이터 준비 → 준비 → 콜백 → NCA 영상 제작`
- 콜백 HTTP 노드 onError: continueRegularOutput (콜백 실패해도 메인 흐름 계속)
- 대상: 3개 워크플로우 전부

### 6. 콜백 준비 노드 수동실행 호환 (`bc8728e`)
- 수동 실행 시 productionId 없어서 `return []` → 워크플로우 멈추는 문제 수정
- 10개 콜백 준비 노드: `return []` → `return [{ json: { skipped: true, status: 'no_productionId' } }]`
- 실패 콜백 HTTP 노드: onError=continueRegularOutput 추가
- 대상: Jay+Mike, 할머니+Mike

### 7. NCA 영상 제작 body 전송 방식 수정 (`e9334f8`)
- `specifyBody: "json"` → `specifyBody: "string"` 변경 (n8n 이중 JSON 파싱 방지)
- `jsonBody` → `body` 키 변경
- `Content-Type: application/json` 헤더 명시적 추가
- 대상: Jay+Mike, 할머니+Mike

### 8. 노드 위치 재배치 (`c276fc1`, `0e74e34`)
- 3개 워크플로우 전체 노드 레이아웃 정리 (단계별 그리드 배치)
- n8n 서버에서 최신 JSON 동기화
- 대상: 3개 워크플로우 전부

## 테스트 결과

### 실행 1235 (할머니+Mike, 수동 실행)
- Execute Workflow 버튼 트리거, productionId 없음
- 51개 노드 전부 success
- 콜백 준비 → `{ skipped: true }` → HTTP 콜백 500 (undefined ID) → continueRegularOutput → 멈추지 않고 끝까지 진행
- **수동 실행 호환 검증 완료**

### 실행 1236 (할머니+Mike, Webhook)
- curl 트리거, productionId: `test-callback-verify-002`
- 51개 노드 전부 success, 영상 3개 모두 성공
- 중간 콜백 직렬 실행 **전체 검증 완료**:

| 콜백 | 실행 | productionId | status |
|---|---|---|---|
| 스크립트 콜백 | OK | test-callback-verify-002 | script_ready |
| 이미지 콜백 | OK | test-callback-verify-002 | images_ready |
| 영상 콜백 | OK | test-callback-verify-002 | videos_ready |
| 렌더링 콜백 | OK | test-callback-verify-002 | rendering |
| 실패 콜백 | OK | test-callback-verify-002 | failed |

### 실행 1247 (할머니+Mike, NCA 수정 테스트)
- NCA body 전송 방식 수정 후 테스트
- 영상 3개 모두 성공
- NCA 데이터 준비에서 "영상4 URL 없음 - 3세그먼트(24초) 필수" 에러 발생
- NCA 영상 제작 노드는 도달하지 못함 (데이터 준비 단계 실패)
- **기존 NCA 로직 이슈** (body 수정과 무관)

## 알려진 이슈

### Google Sheets OAuth 토큰 만료
- 실행 1221에서 `시트 기록` 노드 에러: "authorization grant is invalid, expired, revoked"
- **조치 필요**: n8n 에디터 → Credentials → Google Sheets → 재연결

### TTS 콜백 노드 없음
- 할머니+Mike 워크플로우에 TTS 콜백 준비/TTS 콜백 노드 없음
- Veo3가 직접 음성 생성하는 구조라 TTS 미사용 → 의도된 것일 수 있음
- 필요 시 추가 검토

### NCA 데이터 준비 "영상4 URL 없음" 에러
- 실행 1247에서 발생: "영상4 URL 없음 - 3세그먼트(24초) 필수"
- NCA 데이터 준비 코드가 영상 4개를 기대하지만 3개만 존재
- **조사/수정 필요**

### n8n 병렬 분기 제한
- n8n은 wait/polling 노드가 있는 경로에서 이전 노드의 병렬 side branch를 실행하지 않음
- 중간 콜백은 반드시 메인 파이프라인에 직렬로 삽입해야 함

## 흑형스포츠 vs Jay+Mike/할머니+Mike 차이
- 흑형스포츠는 v86.4 미적용 (실패체크가 "원본 이미지 폴백" 패턴)
- Jay+Mike/할머니+Mike는 v86.4 적용 (실패체크가 "1회 재시도 → throw" 패턴)
- v86.6 + 재시도 버그 수정은 3개 모두 적용됨
- 콜백 수동실행 호환은 Jay+Mike, 할머니+Mike만 적용 (흑형스포츠 미적용)
- NCA body 수정은 Jay+Mike, 할머니+Mike만 적용 (흑형스포츠 미적용)

## 인프라 참고
- n8n URL: `https://n8n.srv1345711.hstgr.cloud`
- API 업로드 시 `name`, `nodes`, `connections`, `settings` 키만 전송
- 업로드 후 반드시 n8n 에디터 F5 새로고침
