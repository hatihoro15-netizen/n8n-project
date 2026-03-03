'use strict';

const express = require('express');
const config = require('./config');
const { capturePreset, captureAdvanced } = require('./capturer');
const { ensureBucket } = require('./uploader');
const { closeBrowser } = require('./browser');
const { listPresetIds } = require('./presets');

const app = express();
app.use(express.json());

/**
 * 헬스체크 엔드포인트
 */
app.get('/health', (_req, res) => {
  res.json({ status: 'ok', presets: listPresetIds().length });
});

/**
 * 캡처 엔드포인트 (v1 프리셋 + v2 어드밴스드 통합)
 * POST /capture
 *
 * v1 (하위 호환):
 *   Body: { capture_id, capture_params?, viewport? }
 *   Response: { url, capture_id, timestamp, dimensions }
 *
 * v2 (신규):
 *   Body: { url, job_id?, filename?, capture_mode?, selector?,
 *           style_mode?, style_args?, omitBackground?, viewport? }
 *   Response: { url, capture_mode, style_mode, selector, timestamp, bytes }
 */
app.post('/capture', async (req, res) => {
  const {
    capture_id,
    capture_params,
    url,
    job_id,
    filename,
    capture_mode,
    selector,
    style_mode,
    style_args,
    omitBackground,
    viewport,
  } = req.body;

  // v2 경로: url 또는 capture_mode/style_mode가 직접 지정된 경우
  const isAdvanced = url || capture_mode || style_mode;

  if (!capture_id && !isAdvanced) {
    return res.status(400).json({
      error: 'capture_id or url is required',
      available: listPresetIds(),
    });
  }

  try {
    if (capture_id && !isAdvanced) {
      // v1 하위 호환: 기존 프리셋 캡처
      const result = await capturePreset({ capture_id, capture_params, viewport });
      return res.json(result);
    }

    // v2 어드밴스드 캡처
    const result = await captureAdvanced({
      url,
      job_id,
      filename,
      capture_mode,
      selector,
      style_mode,
      style_args,
      omitBackground,
      viewport,
    });
    return res.json(result);
  } catch (err) {
    console.error(`[CAPTURE ERROR] ${capture_id || url || 'unknown'}:`, err.message);
    return res.status(500).json({
      error: err.message,
      capture_id: capture_id || null,
    });
  }
});

/**
 * 서버 시작 + MinIO 버킷 초기화
 */
async function start() {
  try {
    await ensureBucket();
    console.log(`[INIT] MinIO bucket "${config.minio.bucket}" ready`);
  } catch (err) {
    console.warn(`[INIT] MinIO bucket check failed: ${err.message} (will retry on first upload)`);
  }

  app.listen(config.port, () => {
    console.log(`[CAPTURE SERVICE] Running on port ${config.port}`);
    console.log(`[CAPTURE SERVICE] Target: ${config.captureBaseUrl}`);
    console.log(`[CAPTURE SERVICE] Presets: ${listPresetIds().length}`);
  });
}

/**
 * Graceful shutdown
 */
async function shutdown() {
  console.log('[SHUTDOWN] Closing browser...');
  await closeBrowser();
  process.exit(0);
}

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);

start();
