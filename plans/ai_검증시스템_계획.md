# AI 콘텐츠 검증 시스템 구현 계획

## Context
현재 숏폼 워크플로우는 AI가 주제를 생성하면 검증 없이 바로 영상 제작에 들어감. 트렌드 분석, 채널 성과 분석, 콘텐츠 품질 검증 과정을 추가하여 알고리즘에 잘 맞는 영상만 제작되도록 개선.

## 핵심 구조: 2개 워크플로우

### 1. 채널 성과 분석 워크플로우 (신규, 매일 1회)
YouTube API로 데이터 수집 → Gemini가 분석 리포트 생성 → Google Sheets에 저장

```
[Cron 06:00] → [4개 채널 루프]
  ├── YouTube API: 우리 채널 최근 Shorts 조회수/좋아요/댓글
  ├── YouTube API: 니치 관련 인기 Shorts 트렌드 검색
  └── Gemini: 성과+트렌드 분석 리포트 생성 → Sheets 저장
```

**리포트 내용:**
- 추천 주제 3개, 피해야 할 주제
- 효과적인 제목/훅(첫 3초) 팁
- 현재 트렌드 각도
- 우리 채널 고성과 영상 패턴

### 2. 기존 숏폼 워크플로우 수정 (4개 채널)
주제 생성 전 리포트 읽기 + 생성 후 AI 검증 + 탈락시 최대 3회 재생성

```
[트리거] → [Sheets에서 분석 리포트 읽기] → [Sub-WF: 주제생성+검증 호출] → [시트 기록] → (기존 영상 제작)
```

### 3. 주제생성+검증 Sub-Workflow (신규)
```
[Trigger] → [AI 주제 생성 1차 (리포트 기반)] → [파싱] → [AI 검증 (점수 매기기)]
  ├── 통과 (7점 이상) → Return 결과
  └── 탈락 → [AI 주제 생성 2차 (피드백 반영)] → [파싱] → [AI 검증]
       ├── 통과 → Return 결과
       └── 탈락 → [AI 주제 생성 3차] → [파싱] → [AI 검증]
            ├── 통과 → Return 결과
            └── 탈락 → 최고점 주제 선택 → Return
```

**AI 검증 6개 항목 (각 1~10점):**
1. 훅 파워 - 첫 문장이 스크롤을 멈추게 하는가
2. 주제 관련성 - 트렌드/추천주제와 맞는가
3. 나레이션 품질 - 자연스럽고 적정 분량인가
4. 클릭 유도력 - 제목이 호기심을 유발하는가
5. 타겟 적합도 - 채널 오디언스에 맞는가
6. 차별화 - 이전 주제와 중복 안 되는가

## 구현 순서

### Phase 1: 분석 인프라 (Google Sheets 탭 + 채널 ID 확인)
- 4개 시트에 `분석리포트` 탭 추가
- YouTube Channel ID 확인 필요

### Phase 2: 채널 성과 분석 워크플로우 생성
- `create_analysis_workflow.py` 작성
- YouTube Data API v3 호출 (search/list, videos/list)
- Gemini 리포트 생성
- 일일 API 비용: ~804 유닛 (한도 10,000의 8%)

### Phase 3: 주제생성+검증 Sub-Workflow 생성
- `create_validation_subworkflow.py` 작성
- 3회 시도 직선 구조 (n8n 루프 제한 우회)
- 검증 프롬프트 + 점수 기준 설정

### Phase 4: 기존 4개 숏폼 워크플로우 수정
- `update_shortform_with_validation.py` 작성
- 분석 리포트 읽기 노드 추가
- Execute Sub-Workflow 노드 연결
- 루믹스 먼저 테스트 → 나머지 3개 적용

### Phase 5: 모니터링 및 튜닝
- 검증 이력 로깅
- 점수 기준 조정 (7점이 적절한지)

## 비용 영향
- Gemini 추가 호출: 최대 6회/영상 (생성 3회 + 검증 3회) → 무료 플랜 내
- YouTube API: 일 804 유닛 추가 → 한도 내
- 영상 제작 비용 변화 없음 (검증 통과 후에만 제작)

## 필요한 사전 확인
- 4개 YouTube 채널 Channel ID
- 채널에 기존 영상이 있는지 (없으면 초기 더미 리포트 수동 입력)

## 수정할 파일/워크플로우
- 신규: 분석 워크플로우 1개
- 신규: Sub-Workflow 1개 (4채널 공용)
- 수정: 4개 숏폼 워크플로우 (연결 변경 + 리포트 읽기 노드 추가)
- 신규 스크립트: `create_analysis_workflow.py`, `create_validation_subworkflow.py`, `update_shortform_with_validation.py`
