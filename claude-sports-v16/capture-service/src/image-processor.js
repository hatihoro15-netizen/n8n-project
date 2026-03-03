'use strict';

const sharp = require('sharp');

const TARGET_WIDTH = 1080;
const TARGET_HEIGHT = 1920;

/**
 * 캡처 이미지를 처리
 * - skipResize=false (기본): 1080x1920 세로 해상도로 크롭/패드 처리
 * - skipResize=true: 리사이즈 없이 PNG 최적화만 수행 (element/long 캡처용)
 * @param {Buffer} inputBuffer - 원본 PNG 버퍼
 * @param {Object} [options={}] - 처리 옵션
 * @param {boolean} [options.skipResize=false] - true이면 리사이즈 건너뜀
 * @returns {Promise<Buffer>} 처리된 PNG 버퍼
 */
async function processImage(inputBuffer, options = {}) {
  const { skipResize = false } = options;

  if (skipResize) {
    return await sharp(inputBuffer)
      .png({ quality: 90 })
      .toBuffer();
  }

  const processed = await sharp(inputBuffer)
    .resize(TARGET_WIDTH, TARGET_HEIGHT, {
      fit: 'contain',
      background: { r: 0, g: 0, b: 0, alpha: 1 },
    })
    .png({ quality: 90 })
    .toBuffer();

  return processed;
}

module.exports = { processImage, TARGET_WIDTH, TARGET_HEIGHT };
