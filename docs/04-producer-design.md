# 04-producer-design.md — n8n 워크플로우 설계

## Producer 워크플로우 (작업 등록)

### 노드 구성
```
[1. Webhook] → [2. Validate] → [3. Create Job] → [4. Save Media] → [5. Queue Push] → [6. Response]
                     ↘ [2-1. Error Response]
```

### 1. Webhook (트리거)
- Method: POST
- Path: /ao/submit
- Body: JSON (입력 스키마 전체)

### 2. Validate (Code 노드)
필수값 검사:
- prompt_p1: 비어있으면 거부
- topic, keywords, category: 비어있으면 거부
- use_media: auto/forced/off 중 하나
- upload_target: 비어있으면 거부
- use_media=forced인데 images/ref_video 없으면 거부
- images[1..4]: URL 형식 검증 (있을 때만)

### 3. Create Job (Supabase)
```sql
INSERT INTO jobs (
  prompt_p1, translate_mode, topic, keywords, category,
  use_media, template_id, upload_target,
  metadata_title, metadata_desc, metadata_tags,
  status
) VALUES (...)
RETURNING id, status, created_at;
```

### 4. Save Media (반복)
images[1..4], ref_video가 있으면 job_media에 삽입:
- images[0] → slot='IMG_1', type='image'
- images[3] → slot='IMG_4', type='image'
- ref_video → slot='REF_VIDEO', type='video'

### 5. Queue Push
- DB 기반 큐 (jobs 테이블의 status=queued를 Worker가 폴링)
- 별도 큐 인프라 불필요

### 6. Response
```json
{
  "success": true,
  "job_id": "uuid",
  "status": "queued",
  "message": "Job registered. Poll /ao/status/{job_id} for updates."
}
```

---

## Worker 워크플로우 (작업 처리, 1건씩)

### 노드 구성
```
[1. Cron/Trigger] → [2. Pop Job] → [3. AO 조립] → [4. 이미지 생성]
→ [5. TTS] → [6. Creatomate 렌더] → [7. 썸네일] → [8. YouTube 업로드]
→ [9. 상태 업데이트] → [10. 로그 기록]
     ↘ [Error Handler: 3회 재시도 / failed]
```

### 2. Pop Job
```sql
SELECT * FROM jobs
WHERE status = 'queued'
ORDER BY created_at
LIMIT 1
FOR UPDATE SKIP LOCKED;
```
→ 즉시 status='processing' 업데이트

### 3. AO 프롬프트 조립
- P1 원문 100% 유지
- 슬롯 주입: {TOPIC}, {KEYWORDS}, {CATEGORY}, {IMG_1}~{IMG_4}, {REF_VIDEO}
- 한글 감지 → translate_mode에 따라 영문 번역 생성
- prompt_to_engine에 최종 프롬프트 저장

### 4. 이미지 생성 (조건부)
- use_media=off 또는 이미지 이미 있으면 → 스킵
- Replicate API 호출 → Supabase Storage 저장

### 5. TTS (ElevenLabs)
- 스크립트 텍스트 → 음성 생성
- Supabase Storage에 오디오 저장

### 6. Creatomate 렌더링
- template_id로 템플릿 선택
- 이미지/오디오/자막 슬롯에 값 주입
- 폴링 → 완료 시 영상 URL 획득

### 7. 썸네일 생성 (선택)
- Ideogram/SDXL로 AI 썸네일 생성

### 8. YouTube 업로드
- OAuth 2.0 토큰으로 업로드
- 메타데이터 (제목/설명/태그/공개설정)

### Error Handler
- 실패 시 retry_count++ (최대 3회)
- 3회 초과 → status='failed' + error_message 기록

---

## 상태 조회 워크플로우

```
GET /ao/status/{job_id}
→ { "job_id": "...", "status": "processing", "video_url": null, "upload_url": null }
```

---

## n8n Webhook 엔드포인트 (개별 기능)

| 트리거 | URL | 데이터 |
|--------|-----|--------|
| 이미지 생성 | /webhook/generate-image | 모델, 프롬프트, 개수 |
| 나레이션 생성 | /webhook/generate-script | 주제, 유형, 톤, AI 모델 |
| 영상 제작 | /webhook/make-video | 이미지, 스크립트, 목소리, 템플릿 |
| 업로드 | /webhook/upload-video | 영상, 제목, 예약시간 |
