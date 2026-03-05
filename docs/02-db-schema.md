# 02-db-schema.md — DB 테이블 설계 (Postgres)

> 구글 시트 사용 금지. 상태/로그 전부 DB.

## 접속 정보
- 컨테이너: n8n-postgres
- 접속: docker exec n8n-postgres psql -U n8n -d n8ndb

## 테이블

### jobs (Job 상태 관리)
```sql
CREATE TABLE ao_jobs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  status        VARCHAR(20) NOT NULL DEFAULT 'queued',
  -- queued / processing / generated / uploading / uploaded / failed / retrying
  prompt_p1     TEXT NOT NULL,
  prompt_final  TEXT,
  translate_mode VARCHAR(10) DEFAULT 'auto',
  topic         VARCHAR(500) NOT NULL,
  keywords      VARCHAR(1000) NOT NULL,
  category      VARCHAR(100) NOT NULL,
  use_media     VARCHAR(10) NOT NULL DEFAULT 'auto',
  proxy_profile VARCHAR(20) DEFAULT 'auto-rotate',
  upload_target VARCHAR(100) NOT NULL,
  metadata_title TEXT,
  metadata_desc  TEXT,
  metadata_tags  TEXT,
  video_out_url TEXT,
  upload_url    TEXT,
  error_message TEXT,
  retry_count   INT DEFAULT 0,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);
```

### job_media (미디어 파일 매핑)
```sql
CREATE TABLE ao_job_media (
  id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id   UUID NOT NULL REFERENCES ao_jobs(id),
  slot     VARCHAR(20) NOT NULL,
  -- IMG_1, IMG_2, IMG_3, IMG_4, REF_VIDEO
  media_url TEXT NOT NULL,
  media_type VARCHAR(20) NOT NULL,
  -- image / video
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### job_logs (실행 로그)
```sql
CREATE TABLE ao_job_logs (
  id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id    UUID NOT NULL REFERENCES ao_jobs(id),
  step      VARCHAR(50) NOT NULL,
  -- validate / assemble / seedance_submit / seedance_poll / upload / complete / error
  message   TEXT,
  detail    JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### proxy_pool (프록시 목록)
```sql
CREATE TABLE ao_proxy_pool (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  proxy_url  TEXT NOT NULL,
  status     VARCHAR(10) DEFAULT 'active',
  -- active / inactive / cooldown
  last_used  TIMESTAMPTZ,
  fail_count INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```
