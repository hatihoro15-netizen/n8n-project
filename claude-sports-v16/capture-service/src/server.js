'use strict';

const express = require('express');
const config = require('./config');
const { capturePreset } = require('./capturer');
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
 * 캡처 엔드포인트
 * POST /capture
 * Body: { capture_id: string, capture_params?: object, viewport?: {w: number, h: number} }
 * Response: { url, capture_id, timestamp, dimensions }
 */
app.post('/capture', async (req, res) => {
  const { capture_id, capture_params, viewport } = req.body;

  if (!capture_id) {
    return res.status(400).json({
      error: 'capture_id is required',
      available: listPresetIds(),
    });
  }

  try {
    const result = await capturePreset({ capture_id, capture_params, viewport });
    return res.json(result);
  } catch (err) {
    console.error(`[CAPTURE ERROR] ${capture_id}:`, err.message);
    return res.status(500).json({
      error: err.message,
      capture_id,
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
