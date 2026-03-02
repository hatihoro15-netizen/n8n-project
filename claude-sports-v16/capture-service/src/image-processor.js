'use strict';

const sharp = require('sharp');

const TARGET_WIDTH = 1080;
const TARGET_HEIGHT = 1920;

/**
 * 캡처 이미지를 1080x1920 세로 해상도로 크롭/패드 처리
 * - 원본 비율을 유지하면서 세로 프레임에 맞춤
 * - 남는 영역은 검정 배경으로 채움
 * @param {Buffer} inputBuffer - 원본 PNG 버퍼
 * @returns {Promise<Buffer>} 처리된 PNG 버퍼
 */
async function processImage(inputBuffer) {
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
