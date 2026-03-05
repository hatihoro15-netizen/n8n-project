# 03-api-integration.md — 외부 API 연동 스펙

## API 목록

| 서비스 | 용도 | 인증 |
|--------|------|------|
| Replicate | 이미지 생성 (Flux Pro/SDXL/Ideogram/Playground v2.5) | API Key |
| Claude API | 스크립트/나레이션 생성 | API Key |
| OpenAI (GPT-4o) | 스크립트/나레이션 생성 | API Key |
| ElevenLabs | TTS 음성 생성 | API Key |
| Creatomate | 영상 렌더링 (씬 합성, 자막) | API Key |
| YouTube | 업로드 | OAuth 2.0 |

## Replicate API (이미지 생성)

### 엔드포인트
```
POST https://api.replicate.com/v1/predictions
Authorization: Bearer {REPLICATE_API_KEY}
```

### 지원 모델
- `black-forest-labs/flux-pro` — 고품질 범용
- `stability-ai/sdxl` — 스타일 다양성
- `ideogram-ai/ideogram-v2` — 텍스트 포함 이미지
- `playgroundai/playground-v2.5` — 포토리얼리스틱

### 흐름
1. POST /predictions → prediction_id 반환
2. GET /predictions/{id} 폴링 → status=succeeded → output URL

## ElevenLabs API (TTS)

### 엔드포인트
```
POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}
xi-api-key: {ELEVENLABS_API_KEY}
```

### 파라미터
- text, voice_id, model_id
- voice_settings: stability, similarity_boost, speed

### 흐름
동기 응답 — 오디오 바이너리 직접 반환 (mp3)

## Creatomate API (영상 렌더링)

### 엔드포인트
```
POST https://api.creatomate.com/v1/renders
Authorization: Bearer {CREATOMATE_API_KEY}
```

### 파라미터
- template_id: Creatomate 템플릿 ID
- modifications: 슬롯별 값 교체 (이미지, 텍스트, 오디오)

### 흐름
1. POST /renders → render_id 반환
2. GET /renders/{id} 폴링 → status=succeeded → url

## Claude / OpenAI API (텍스트 AI)

### Claude
```
POST https://api.anthropic.com/v1/messages
x-api-key: {CLAUDE_API_KEY}
anthropic-version: 2023-06-01
```

### OpenAI
```
POST https://api.openai.com/v1/chat/completions
Authorization: Bearer {OPENAI_API_KEY}
```

## YouTube Data API (업로드)

### 인증: OAuth 2.0
1. 사용자 동의 → authorization code
2. code → access_token + refresh_token
3. 토큰 만료 시 자동 갱신

### 업로드
```
POST https://www.googleapis.com/upload/youtube/v3/videos
Authorization: Bearer {ACCESS_TOKEN}
```
- part: snippet,status
- snippet: title, description, tags, categoryId
- status: privacyStatus (public/private/unlisted), publishAt (예약)

## 비용 추정 (월 $150~300 예산)

| 서비스 | 단가 (대략) | 일 3건 기준 |
|--------|------------|-----------|
| Replicate | ~$0.05/이미지 | ~$4.5/월 |
| ElevenLabs | ~$0.30/1000자 | ~$27/월 |
| Creatomate | ~$0.50/렌더 | ~$45/월 |
| Claude/OpenAI | ~$0.02/요청 | ~$1.8/월 |
| **합계** | | **~$78/월** |

## 자동 재시도 정책
- 모든 API 호출: 실패 시 3회 재시도
- 재시도 간격: 5초 → 15초 → 45초 (지수 백오프)
- 3회 초과 → failed 상태 + 수동 재시도 버튼
