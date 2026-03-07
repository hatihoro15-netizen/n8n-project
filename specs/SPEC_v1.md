# SPEC v1

## 1. 우선순위 (절대)
1. Prompt (`prompt_p1`)
2. Narration (`narration_text`, `narration_style`, `narration_tone`)
3. Audio (`bgm`, `sfx`)
4. Metadata (`topic`, `keywords`, `category`)는 저장/검색용만 사용

## 2. 길이 제한
- 숏폼: 최대 30초
- 롱폼: 최대 120초

## 3. 저작권 원칙
- 외부 소스 자동 수집 금지
- 사용자 업로드 오디오만 사용
- 업로드가 없으면 무음 또는 기본 내장 에셋(명시된 것만) 사용

## 4. 나레이션 원칙
- `narration_text` 입력 시 최우선 사용
- 미입력 시 `prompt_p1` 기반 생성
- 길이는 `duration_sec`에 맞게 자동 압축/확장
- `topic/keywords/category`는 나레이션 생성에 영향 금지

## 5. 엔진 분리
- `character_story`: 캐릭터 서사 중심
- `core_message`: 핵심만 빠르게 전달
- `live_promo`: 실시간 방송 느낌 홍보
- `meme`: 짧고 강렬한 밈
- `action_sports`: 박진감 액션/스포츠

## 6. 합격 기준 (테스트)
- Prompt 충실도: 4/5 이상
- Narration 자연스러움: 4/5 이상
- 길이 준수: 100% 통과
- 오디오 적합성: 4/5 이상
- 엔진 구분도(같은 입력 비교): 차별성 4/5 이상
