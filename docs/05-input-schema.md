# 05-input-schema.md — 입력 스키마 정의

## 필드 정의

| 필드 | 필수 | 타입 | 설명 |
|------|------|------|------|
| prompt_p1 | Y | string | 원문 지침 (절대 변경 금지) |
| translate_mode | N | string | 한글→영문 처리. auto(기본)/on/off |
| topic | Y | string | 주제 (1줄 정의) |
| keywords | Y | string | 키워드 (쉼표 구분) |
| category | Y | string | 카테고리 |
| images[1..4] | N | string[] | 이미지 URL 1~4개. 슬롯 자동 매핑 |
| ref_video | N | string | 레퍼런스 영상 URL |
| use_media | Y | string | auto / forced / off |
| template_id | N | string | 영상 템플릿 선택 (뉴스/광고/스토리 등) |
| upload_target | Y | string | YouTube |
| metadata.title | N | string | 영상 제목 |
| metadata.description | N | string | 영상 설명 |
| metadata.tags | N | string | 태그 (쉼표 구분) |

## 파생 필드 (자동 생성)
| 필드 | 설명 |
|------|------|
| prompt_lang_detected | 언어 감지 결과 (ko/en/...) |
| prompt_en | 영문 복사용 프롬프트 |
| prompt_to_engine | 실제 엔진에 전달된 최종 프롬프트 |

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
- topic: 비어있으면 400 에러
- keywords: 비어있으면 400 에러
- category: 비어있으면 400 에러
- use_media: auto/forced/off 중 하나가 아니면 400 에러
- upload_target: 비어있으면 400 에러
- images: 최대 4개, 각 URL 형식 검증
- use_media=forced인데 images/ref_video 없으면 400 에러
