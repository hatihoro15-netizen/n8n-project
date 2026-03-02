'use strict';

const puppeteer = require('puppeteer-core');
const config = require('./config');

/** @type {import('puppeteer-core').Browser|null} */
let browserInstance = null;

/**
 * Puppeteer 브라우저 싱글턴 반환 (콜드스타트 2-5초 방지)
 * 요청마다 새 탭(page)을 열어 병렬 캡처 가능
 * @returns {Promise<import('puppeteer-core').Browser>}
 */
async function getBrowser() {
  if (browserInstance && browserInstance.connected) {
    return browserInstance;
  }

  browserInstance = await puppeteer.launch({
    executablePath: config.chromiumPath,
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--font-render-hinting=none',
    ],
  });

  browserInstance.on('disconnected', () => {
    browserInstance = null;
  });

  return browserInstance;
}

/**
 * 브라우저 인스턴스 종료 (서버 shutdown 시 호출)
 * @returns {Promise<void>}
 */
async function closeBrowser() {
  if (browserInstance && browserInstance.connected) {
    await browserInstance.close();
    browserInstance = null;
  }
}

module.exports = { getBrowser, closeBrowser };
