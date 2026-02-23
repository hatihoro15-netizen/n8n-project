# n8n 워크플로우 AI 프롬프트 업데이트 (v7 → v8.2)

## 작업 개요
두 워크플로우의 "AI 콘텐츠 생성" 노드(Gemini 호출 노드)의 프롬프트를 v8.2로 교체한다.

## 대상 워크플로우

| 워크플로우 | ID | 프롬프트 파일 |
|---|---|---|
| Jay+Mike | jSEDYrkFcWUzJ8Et | prompt_jay_mike_v8.2_final.md |
| 할머니+Mike | jRT8nmDr34S96I1b | prompt_grandma_mike_v8.2_final.md |

## n8n API 정보
- API URL: https://n8n.srv1345711.hstgr.cloud/api/v1
- API Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4

## 작업 순서

### 1단계: 현재 프롬프트 백업
각 워크플로우의 현재 AI 콘텐츠 생성 노드 프롬프트를 파일로 백업해둘 것.

### 2단계: 프롬프트 교체
- Jay+Mike (jSEDYrkFcWUzJ8Et) → prompt_jay_mike_v8.2_final.md 내용으로 교체
- 할머니+Mike (jRT8nmDr34S96I1b) → prompt_grandma_mike_v8.2_final.md 내용으로 교체

주의: 프롬프트 내의 `{{ $json.categoryName }}`, `{{ $json.currentTopic }}` 변수는 n8n 표현식이므로 절대 수정하지 말 것.

### 3단계: 교체 확인
교체 후 각 워크플로우에서 AI 콘텐츠 생성 노드의 프롬프트 첫 5줄을 출력해서 정상 교체되었는지 확인.

## v8.2 주요 변경사항 (v7 대비)
1. 7턴 고정 순서 추가 (B→A / B→A→B / A→B)
2. 역할 배타 규칙 표 추가
3. 카테고리별 톤 가이드 4종 추가
4. 필수 단어장 강화
5. 호구썰 5가지 소재 제한
6. 출력 형식 강화 (코드블록 금지, 순수 JSON만)
7. 출력 예시를 스켈레톤으로 변경 (AI 복사 방지)
8. 장면2 4턴 모호표현 금지 규칙 추가
9. Subject 구체적 작성 규칙 추가
10. 검증 체크리스트 + 변주 포인트 추가
11. 한글 외래어 활용 규칙 추가
