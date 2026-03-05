-- AO 영상자동화 시스템 — Supabase PostgreSQL 초기화 SQL
-- 실행 위치: Supabase Dashboard > SQL Editor
-- 작성일: 2026-03-05

-- ========================================
-- 1. jobs 테이블 (Job 상태/메타데이터)
-- ========================================
CREATE TABLE IF NOT EXISTS jobs (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  prompt_p1           TEXT NOT NULL,               -- 원문 지침 (절대 변경 금지)
  topic               TEXT NOT NULL,
  keywords            TEXT NOT NULL,
  category            TEXT NOT NULL,
  use_media           TEXT NOT NULL DEFAULT 'auto', -- auto/forced/off
  upload_target       TEXT NOT NULL DEFAULT 'youtube',
  template_id         TEXT,
  image_slots         JSONB DEFAULT '{}',           -- {IMG_1, IMG_2, IMG_3, IMG_4}
  ref_video           TEXT,
  metadata            JSONB DEFAULT '{}',           -- 제목/설명/태그
  -- 파생 필드 (자동 생성)
  prompt_lang_detected TEXT DEFAULT 'ko',
  needs_translation   BOOLEAN DEFAULT FALSE,
  prompt_en           TEXT,                         -- 영문 복사용
  prompt_to_engine    TEXT,                         -- 실제 엔진에 전달된 최종 프롬프트
  -- 처리 결과
  generated_images    JSONB DEFAULT '[]',
  rendered_video_url  TEXT,
  render_id           TEXT,
  youtube_video_id    TEXT,
  youtube_url         TEXT,
  -- 상태 관리
  status              TEXT NOT NULL DEFAULT 'queued',
  -- queued / processing / generated / uploading / uploaded / failed / retrying
  retry_count         INT NOT NULL DEFAULT 0,
  last_error          TEXT,
  -- 타임스탬프
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at        TIMESTAMPTZ
);

-- jobs 인덱스
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at DESC);

-- ========================================
-- 2. job_media 테이블 (미디어 파일 매핑)
-- ========================================
CREATE TABLE IF NOT EXISTS job_media (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id      UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  media_type  TEXT NOT NULL,  -- image/audio/video/thumbnail
  slot_name   TEXT,           -- IMG_1 ~ IMG_4
  file_url    TEXT NOT NULL,
  file_name   TEXT,
  file_size   BIGINT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_job_media_job_id ON job_media(job_id);

-- ========================================
-- 3. job_logs 테이블 (실행 로그/에러)
-- ========================================
CREATE TABLE IF NOT EXISTS job_logs (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id      UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  level       TEXT NOT NULL DEFAULT 'info',  -- info/warn/error
  message     TEXT NOT NULL,
  detail      JSONB,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_job_logs_job_id ON job_logs(job_id);
CREATE INDEX IF NOT EXISTS idx_job_logs_created_at ON job_logs(created_at DESC);

-- ========================================
-- 4. templates 테이블 (영상 템플릿)
-- ========================================
CREATE TABLE IF NOT EXISTS templates (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name                TEXT NOT NULL,
  description         TEXT,
  style               TEXT,         -- news/ad/story
  aspect_ratio        TEXT NOT NULL DEFAULT '9:16',  -- 9:16 / 16:9
  creatomate_id       TEXT,         -- Creatomate 템플릿 ID
  preview_url         TEXT,
  is_active           BOOLEAN NOT NULL DEFAULT TRUE,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 기본 템플릿 데이터
INSERT INTO templates (name, description, style, aspect_ratio) VALUES
  ('쇼츠 기본', '기본 쇼츠 템플릿 (9:16)', 'story', '9:16'),
  ('뉴스 스타일', '뉴스 스타일 쇼츠', 'news', '9:16'),
  ('광고 스타일', '광고 스타일 쇼츠', 'ad', '9:16'),
  ('일반 영상', '일반 가로형 영상 (16:9)', 'story', '16:9')
ON CONFLICT DO NOTHING;

-- ========================================
-- 5. sources 테이블 (소스 라이브러리)
-- ========================================
CREATE TABLE IF NOT EXISTS sources (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,
  type        TEXT NOT NULL,  -- image/audio/video
  file_url    TEXT NOT NULL,
  file_size   BIGINT,
  mime_type   TEXT,
  thumbnail_url TEXT,
  use_count   INT NOT NULL DEFAULT 0,
  tags        TEXT[],
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sources_type ON sources(type);

-- ========================================
-- 6. api_connections 테이블 (API 키 관리)
-- ========================================
CREATE TABLE IF NOT EXISTS api_connections (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  service       TEXT NOT NULL UNIQUE,  -- youtube/elevenlabs/replicate/claude/openai/creatomate
  api_key       TEXT,                  -- 암호화 저장 권장
  access_token  TEXT,                  -- OAuth 토큰
  refresh_token TEXT,
  expires_at    TIMESTAMPTZ,
  is_connected  BOOLEAN NOT NULL DEFAULT FALSE,
  last_tested_at TIMESTAMPTZ,
  metadata      JSONB DEFAULT '{}',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 기본 서비스 레코드 생성
INSERT INTO api_connections (service, is_connected) VALUES
  ('youtube', FALSE),
  ('elevenlabs', FALSE),
  ('replicate', FALSE),
  ('claude', FALSE),
  ('openai', FALSE),
  ('creatomate', FALSE)
ON CONFLICT (service) DO NOTHING;

-- ========================================
-- 7. cost_logs 테이블 (API 비용 추적)
-- ========================================
CREATE TABLE IF NOT EXISTS cost_logs (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id      UUID REFERENCES jobs(id) ON DELETE SET NULL,
  service     TEXT NOT NULL,        -- replicate/elevenlabs/creatomate/claude/openai
  operation   TEXT,                 -- image_generation/tts/video_render/script
  cost_usd    NUMERIC(10, 6),       -- 달러 단위
  tokens_used INT,                  -- 토큰 사용량 (LLM인 경우)
  detail      JSONB,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cost_logs_service ON cost_logs(service);
CREATE INDEX IF NOT EXISTS idx_cost_logs_created_at ON cost_logs(created_at DESC);

-- ========================================
-- 8. updated_at 자동 갱신 트리거
-- ========================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_jobs_updated_at
  BEFORE UPDATE ON jobs
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_templates_updated_at
  BEFORE UPDATE ON templates
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_api_connections_updated_at
  BEFORE UPDATE ON api_connections
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ========================================
-- 완료 확인 쿼리
-- ========================================
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('jobs','job_media','job_logs','templates','sources','api_connections','cost_logs')
ORDER BY table_name;
