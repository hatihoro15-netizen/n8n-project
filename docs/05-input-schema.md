# 05-input-schema.md — 입력 스키마 정의

## 필드 정의

| 필드 | 필수 | 타입 | 설명 |
|------|------|------|------|
| prompt_p1 | Y | string | 원문 지침 (절대 변경 금지, 단일 소스) |
| translate_mode | N | string | 한글→영문 처리. auto(기본)/on/off |
| topic | N | string | 주제 (저장/표시 전용, 생성 영향 금지) |
| keywords | N | string | 키워드 (저장/표시 전용, 생성 영향 금지) |
| category | N | string | 카테고리 (저장/표시 전용, 생성 영향 금지) |
| duration | N | int | 목표 길이(초). 허용값: 30/40/50/60/90/120/150/180 |
| strict_mode | N | boolean | Length Gate 하드 차단. false(기본)=보정 우선, true=초과 시 실패 |
| verify_mode | N | boolean | 검증 모드. true 시 output_hash를 job_logs에 기록 |
| images[1..4] | N | string[] | 이미지 URL 1~4개. 슬롯 자동 매핑 |
| ref_video | N | string | 레퍼런스 영상 URL |
| use_media | N | string | auto / forced(기본) / off |
| template_id | N | string | 영상 템플릿 선택 |
| upload_target | N | string | YouTube (기본) |
| metadata.title | N | string | 영상 제목 |
| metadata.description | N | string | 영상 설명 |
| metadata.tags | N | string | 태그 (쉼표 구분) |

## 파생 필드 (자동 생성)
| 필드 | 설명 |
|------|------|
| prompt_lang_detected | 언어 감지 결과 (ko/en/...) |
| prompt_en | 영문 복사용 프롬프트 |
| prompt_to_engine | 실제 엔진에 전달된 최종 프롬프트 |
| prompt_hash | prompt_p1의 FNV-1a 해시 (Prompt Lock용) |

## Prompt Lock
- Producer: prompt_p1의 해시를 prompt_hash 컬럼에 저장
- Worker: assemble-prompt 후 IF 노드로 prompt_lock_valid 분기
  - true: 정상 진행
  - false: "Prompt Lock 재생성" 노드에서 최신 prompt_p1 기준으로 재조립 후 진행
- 렌더 직전: DB에서 prompt_hash 재조회하여 2차 확인 (PROMPT_LOCK_CHANGED 에러 시 재시도)
- prompt_lock_action: none / regenerated
- 해시 알고리즘: FNV-1a (n8n Code 노드 crypto 미지원으로 인한 선택)

## Last-Edit Priority
- 생성 직전 마지막 prompt_p1을 단일 소스로 사용
- topic/keywords/category로 프롬프트 재조합 금지
- topic/keywords/category는 DB 저장 + UI 표시 전용

## Length Gate
- duration 필드로 목표 길이 지정 (허용값: 30/40/50/60/90/120/150/180초)
- 통과 기준:
  - strict_mode=true: target ±1초 (예: 30초 → 29~31초)
  - strict_mode=false: target-3초 ~ target+1초 (예: 30초 → 27~31초)
- 보정 방식: clip_count 재계산 (짧으면 클립 반복, 길면 분할)
- 나레이션 생성 시 target_duration에 맞는 분량 지시 (한국어 4.5자/초 기준)
- TTS 결과가 목표 미만이면 나레이션 재생성 1회 시도, 여전히 짧으면 그대로 진행 + job_logs 기록
- strict_mode=true에서 범위 밖이면 LENGTH_GATE_BLOCKED 에러
- length_gate_status: no_gate / pass / corrected_short / corrected_long / under_soft / over_soft / blocked_short / blocked_long

## Verify Mode
- payload에 verify_mode=true 추가 시 활성화
- 단일 실행 결과의 output_hash를 DB ao_job_logs(detail.output_hash)에 기록
- 10회 반복은 외부 호출자가 동일 payload로 10회 호출하는 구조
- 비교 기준: ao_job_logs에서 동일 prompt_hash의 output_hash 값 일치 여부 확인
- output_hash 생성 입력: prompt_to_engine + production_mode + clip_duration + aspect_ratio + target_duration + tts_text + total_duration

## use_media 모드
- **auto**: 이미지/영상 있으면 활용, 없으면 프롬프트만으로 생성
- **forced**: 제공된 이미지/영상 반드시 함께 사용
- **off**: 프롬프트만 사용 (미디어 무시)

## translate_mode
- **auto** (기본): 한글이면 자동 번역, 영문이면 그대로
- **on**: 항상 영문 번역 생성
- **off**: 번역 없이 원문 그대로 전달

## 이미지 슬롯 매핑
```
images[0] → {IMG_1}
images[1] → {IMG_2}
images[2] → {IMG_3}
images[3] → {IMG_4}
```

## 검증 규칙
- prompt_p1: 비어있으면 400 에러
- duration: 허용값(30/40/50/60/90/120/150/180) 외 400 에러
- images: 최대 4개, 각 URL 형식 검증
- use_media=forced인데 images/ref_video 없으면 400 에러
- topic/keywords/category: 선택 (누락 시 빈 문자열 저장)
