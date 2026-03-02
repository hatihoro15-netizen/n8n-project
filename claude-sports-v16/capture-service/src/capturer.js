'use strict';

const { getBrowser } = require('./browser');
const { processImage, TARGET_WIDTH, TARGET_HEIGHT } = require('./image-processor');
const { uploadCapture } = require('./uploader');
const { getPreset, listPresetIds } = require('./presets');
const config = require('./config');

/**
 * 페이지 캡처 → 이미지 처리 → MinIO 업로드 실행
 * @param {Object} params
 * @param {string} params.capture_id - 프리셋 ID (presets.js에서 매핑)
 * @param {Object} [params.capture_params] - 추가 파라미터 (추후 확장용)
 * @param {Object} [params.viewport] - 커스텀 뷰포트 {w, h}
 * @returns {Promise<{url: string, capture_id: string, timestamp: string, dimensions: {width: number, height: number}}>}
 */
async function capturePreset({ capture_id, capture_params, viewport }) {
  const preset = getPreset(capture_id);
  if (!preset) {
    const available = listPresetIds().join(', ');
    throw new Error(`Unknown capture_id: "${capture_id}". Available: ${available}`);
  }

  const vw = viewport?.w || TARGET_WIDTH;
  const vh = viewport?.h || TARGET_HEIGHT;
  const targetUrl = config.captureBaseUrl + preset.path;

  const browser = await getBrowser();
  const page = await browser.newPage();

  try {
    await page.setViewport({ width: vw, height: vh });
    await page.goto(targetUrl, {
      waitUntil: 'networkidle2',
      timeout: 30000,
    });

    // 페이지 로딩 후 동적 콘텐츠 렌더링 대기
    await page.evaluate(() => new Promise((resolve) => setTimeout(resolve, 2000)));

    const screenshotBuffer = await page.screenshot({
      type: 'png',
      fullPage: false,
    });

    const processedBuffer = await processImage(screenshotBuffer);
    const url = await uploadCapture(processedBuffer, capture_id);
    const timestamp = new Date().toISOString();

    return {
      url,
      capture_id,
      timestamp,
      dimensions: { width: TARGET_WIDTH, height: TARGET_HEIGHT },
    };
  } finally {
    await page.close();
  }
}

module.exports = { capturePreset };
