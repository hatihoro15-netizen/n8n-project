# SPEC v1

## 1. 우선순위 (절대)
1. Prompt (`prompt_p1`)
2. Narration (`narration_text`, `narration_style`, `narration_tone`)
3. Audio (`bgm`, `sfx`)
4. Metadata (`topic`, `keywords`, `category`)는 저장/검색용만 사용

## 2. 길이 제한
- 숏폼: 최대 30초
- 롱폼: 최대 120초
- strict_mode=true: target_duration ±1초
- strict_mode=false: target_duration -3초 이상 (예: 30초 → 최소 27초)

## 3. 저작권 원칙
- 외부 소스 자동 수집 금지
- 사용자 업로드 오디오만 사용
- 업로드가 없으면 무음 처리

## 4. 나레이션 원칙
- `narration_text` 입력 시 최우선 사용
- 미입력 시 `prompt_p1` 기반 생성
- 길이는 `duration_sec`에 맞게 자동 압축/확장
- `topic/keywords/category`는 나레이션 생성에 영향 금지

### narration_style 허용값
| 값 | 설명 |
|---|---|
| `설명형` | 정보 전달 중심 (기본값) |
| `스토리형` | 서사 흐름 중심 |
| `광고형` | 임팩트/CTA 중심 |
| `감성형` | 감정 공감 중심 |

- 미입력 기본값: `설명형`
- 허용값 외 입력 시 400 에러

### narration_tone 허용값
| 값 | 설명 |
|---|---|
| `차분하게` | 안정적이고 신뢰감 있는 톤 (기본값) |
| `흥분되게` | 에너지 넘치고 빠른 톤 |
| `유머러스하게` | 가볍고 재미있는 톤 |
| `긴박하게` | 긴장감 있고 집중하는 톤 |

- 미입력 기본값: `차분하게`
- 허용값 외 입력 시 400 에러

## 5. 엔진 분리

### engine_type 허용값
| 값 | 설명 |
|---|---|
| `character_story` | 캐릭터 서사 중심 |
| `core_message` | 핵심만 빠르게 전달 (기본값) |
| `live_promo` | 실시간 방송 느낌 홍보 |
| `meme` | 짧고 강렬한 밈 |
| `action_sports` | 박진감 액션/스포츠 |

- 미입력 기본값: `core_message`
- 허용값 외 입력 시 400 에러
- Producer에서 engine_type 수신 → job_logs 기록 → IF/Switch 골격 노드로 분기
- 현재는 모두 공통 경로로 합류 (실제 엔진 로직은 Phase 4에서 구현)

## 6. 실패 기준
- 우선순위 원칙 위반 시 결과 폐기
- topic/keywords/category가 생성 로직에 영향을 준 경우 결과 폐기

## 7. 합격 기준 (테스트)
- Prompt 충실도: 4/5 이상
- Narration 자연스러움: 4/5 이상
- 길이 준수: 100% 통과
- 오디오 적합성: 4/5 이상
- 엔진 구분도(같은 입력 비교): 차별성 4/5 이상

## 8. 하드코딩 원칙
- 변경 가능성 있는 값(타임아웃, 클립 길이, 나레이션 계수, 재시도 횟수 등)은 ENV/설정값으로 처리
- 정말 불가피한 경우만 하드코딩 허용 — 이유/영향범위/해제조건 함께 명시
