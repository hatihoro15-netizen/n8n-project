# 04-producer-design.md — n8n Producer 워크플로우 초안 설계

## 개요
웹훅으로 입력을 받아 → 검증 → Job 생성 → Queue Push → job_id 반환

## 노드 구성 (초안)

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
- topic: 비어있으면 거부
- keywords: 비어있으면 거부
- category: 비어있으면 거부
- use_media: auto/forced/off 중 하나
- upload_target: 비어있으면 거부
- images[1..4]: URL 형식 검증 (있을 때만)

검사 실패 → Error Response 분기

### 3. Create Job (Postgres 노드)
```sql
INSERT INTO ao_jobs (
  prompt_p1, translate_mode, topic, keywords, category,
  use_media, proxy_profile, upload_target,
  metadata_title, metadata_desc, metadata_tags,
  status
) VALUES (
  $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, 'queued'
) RETURNING id, status, created_at;
```

### 4. Save Media (Code → Postgres, 반복)
images[1..4], ref_video가 있으면 ao_job_media에 삽입:
```sql
INSERT INTO ao_job_media (job_id, slot, media_url, media_type)
VALUES ($1, $2, $3, $4);
```
- images[1] → slot='IMG_1', type='image'
- images[2] → slot='IMG_2', type='image'
- ...
- ref_video → slot='REF_VIDEO', type='video'

### 5. Queue Push
- 방법 A: n8n 내장 Queue (Execute Workflow Trigger + Wait)
- 방법 B: Postgres 기반 큐 (ao_jobs 테이블의 status=queued를 Worker가 폴링)
- **권장: 방법 B** (별도 인프라 불필요, 단순)

### 6. Response (Webhook Response)
```json
{
  "success": true,
  "job_id": "uuid",
  "status": "queued",
  "message": "Job registered. Poll /ao/status/{job_id} for updates."
}
```

## 입력 스키마 (웹훅 Body)

```json
{
  "prompt_p1": "이 사람이 카메라를 보며 미소 짓는 영상을 만들어줘",
  "translate_mode": "auto",
  "topic": "AI 인물 영상",
  "keywords": "인물, 미소, AI영상",
  "category": "인물",
  "images": ["https://minio.../img1.jpg"],
  "ref_video": null,
  "use_media": "auto",
  "proxy_profile": "auto-rotate",
  "upload_target": "YouTube Shorts",
  "metadata": {
    "title": "AI가 만든 미소 영상",
    "description": "...",
    "tags": "AI,영상,shorts"
  }
}
```

## 상태 조회 엔드포인트 (별도 워크플로우)

```
GET /ao/status/{job_id}
→ { "job_id": "...", "status": "processing", "video_url": null }
```

## Worker 트리거 방식 (다음 단계)
- Worker 워크플로우는 Cron(1분 간격) 또는 Execute Workflow로 트리거
- `SELECT * FROM ao_jobs WHERE status='queued' ORDER BY created_at LIMIT 1 FOR UPDATE SKIP LOCKED`
- 가져온 Job의 status를 즉시 'processing'으로 업데이트
