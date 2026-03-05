# 02-db-schema.md — DB 테이블 설계 (Supabase PostgreSQL)

> 구글 시트 사용 금지. 상태/로그 전부 DB.
> API 키는 암호화 저장, 화면 마스킹.

## 테이블 목록
| 테이블 | 역할 |
|--------|------|
| jobs | Job 상태/메타데이터 |
| job_media | 미디어 파일 매핑 |
| job_logs | 실행 로그/에러 + 비용 |
| templates | 영상 템플릿 관리 |
| sources | 소스 라이브러리 (이미지/오디오/영상) |
| api_connections | API 키 (암호화 저장) |
| cost_logs | API 비용 추적 |

## 테이블 상세

### jobs
```sql
CREATE TABLE jobs (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  status               VARCHAR(20) NOT NULL DEFAULT 'queued',
  -- queued / processing / generated / uploading / uploaded / failed / retrying
  prompt_p1            TEXT NOT NULL,
  prompt_en            TEXT,
  prompt_to_engine     TEXT,
  prompt_lang_detected VARCHAR(10),
  translate_mode       VARCHAR(10) DEFAULT 'auto',
  topic                VARCHAR(500) NOT NULL,
  keywords             VARCHAR(1000) NOT NULL,
  category             VARCHAR(100) NOT NULL,
  use_media            VARCHAR(10) NOT NULL DEFAULT 'auto',
  template_id          UUID REFERENCES templates(id),
  upload_target        VARCHAR(100) NOT NULL DEFAULT 'YouTube',
  metadata_title       TEXT,
  metadata_desc        TEXT,
  metadata_tags        TEXT,
  video_out_url        TEXT,
  thumbnail_url        TEXT,
  upload_url           TEXT,
  error_message        TEXT,
  retry_count          INT DEFAULT 0,
  created_at           TIMESTAMPTZ DEFAULT NOW(),
  updated_at           TIMESTAMPTZ DEFAULT NOW()
);
```

### job_media
```sql
CREATE TABLE job_media (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id     UUID NOT NULL REFERENCES jobs(id),
  slot       VARCHAR(20) NOT NULL,
  -- IMG_1, IMG_2, IMG_3, IMG_4, REF_VIDEO
  media_url  TEXT NOT NULL,
  media_type VARCHAR(20) NOT NULL,
  -- image / video
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### job_logs
```sql
CREATE TABLE job_logs (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id     UUID NOT NULL REFERENCES jobs(id),
  step       VARCHAR(50) NOT NULL,
  -- validate / assemble / image_gen / tts / render / thumbnail / upload / complete / error
  message    TEXT,
  detail     JSONB,
  cost       DECIMAL(10,4),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### templates
```sql
CREATE TABLE templates (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name            VARCHAR(200) NOT NULL,
  type            VARCHAR(20) NOT NULL,
  -- news / ad / story / custom
  aspect_ratio    VARCHAR(10) NOT NULL,
  -- 9:16 / 16:9
  creatomate_id   VARCHAR(100),
  preview_url     TEXT,
  is_active       BOOLEAN DEFAULT true,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### sources
```sql
CREATE TABLE sources (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  type          VARCHAR(20) NOT NULL,
  -- image / audio / video
  file_url      TEXT NOT NULL,
  file_name     VARCHAR(500),
  thumbnail_url TEXT,
  use_count     INT DEFAULT 0,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);
```

### api_connections
```sql
CREATE TABLE api_connections (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  service      VARCHAR(50) NOT NULL,
  -- youtube / elevenlabs / replicate / claude / openai / creatomate
  auth_type    VARCHAR(20) NOT NULL,
  -- oauth / api_key
  credentials  TEXT NOT NULL,
  -- 암호화 저장
  status       VARCHAR(20) DEFAULT 'active',
  last_tested  TIMESTAMPTZ,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);
```

### cost_logs
```sql
CREATE TABLE cost_logs (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id     UUID REFERENCES jobs(id),
  service    VARCHAR(50) NOT NULL,
  -- openai / replicate / elevenlabs / creatomate
  operation  VARCHAR(100),
  cost_usd   DECIMAL(10,4) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```
