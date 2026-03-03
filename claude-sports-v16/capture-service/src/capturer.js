'use strict';

const { getBrowser } = require('./browser');
const { processImage, TARGET_WIDTH, TARGET_HEIGHT } = require('./image-processor');
const { uploadCapture } = require('./uploader');
const { getPreset, listPresetIds } = require('./presets');
const config = require('./config');

/** 뷰포트 최대 높이 상한 (Chrome 안정성) */
const MAX_VIEWPORT_HEIGHT = 16000;

/**
 * 광고/헤더/푸터/사이드바/스크롤바 숨김 CSS 주입
 * @param {import('puppeteer-core').Page} page
 * @returns {Promise<void>}
 */
async function applyCommonCleanup(page) {
  await page.evaluate(() => {
    const style = document.createElement('style');
    style.innerHTML = `
      body::-webkit-scrollbar { display:none; }
      header, footer, .sidebar, .ad, .ad-banner, .popup { display:none !important; }
    `;
    document.head.appendChild(style);
  });
}

/**
 * 스타일 모드별 CSS 주입
 * @param {import('puppeteer-core').Page} page
 * @param {Object} opts
 * @param {string} opts.style_mode - CLEAN | FONT_UP | HIGHLIGHT | ZOOM
 * @param {string} opts.selector - 대상 CSS 셀렉터
 * @param {Object} [opts.style_args] - 추가 스타일 인자 (e.g. { scale: 1.5 })
 * @returns {Promise<void>}
 */
async function applyStyleMode(page, { style_mode, selector, style_args }) {
  if (!style_mode || !selector) return;

  await page.evaluate((mode, sel, args) => {
    const target = document.querySelector(sel);
    if (!target) return;

    if (mode === 'CLEAN') {
      document.body.style.background = 'transparent';
      target.style.background = '#fff';
      target.style.borderRadius = '20px';
      target.style.boxShadow = '0 10px 30px rgba(0,0,0,0.25)';
      target.style.padding = '20px';
    }

    if (mode === 'FONT_UP') {
      target.style.transform = 'scale(1.15)';
      target.style.transformOrigin = 'top left';
      target.querySelectorAll('*').forEach((el) => {
        el.style.fontSize = '120%';
        el.style.fontWeight = '700';
        el.style.color = '#000';
      });
    }

    if (mode === 'ZOOM') {
      const scale = (args && args.scale) ? Number(args.scale) : 1.2;
      target.style.transform = `scale(${scale})`;
      target.style.transformOrigin = 'center';
    }

    if (mode === 'HIGHLIGHT') {
      const overlay = document.createElement('div');
      overlay.style.position = 'fixed';
      overlay.style.inset = '0';
      overlay.style.background = 'rgba(0,0,0,0.7)';
      overlay.style.zIndex = '9998';
      document.body.appendChild(overlay);

      target.style.position = 'relative';
      target.style.zIndex = '9999';
      target.style.background = '#fff';
      target.style.borderRadius = '16px';
      target.style.boxShadow = '0 0 50px rgba(255,255,255,0.35)';
    }
  }, style_mode, selector, style_args || {});
}

/**
 * 엘리먼트의 scrollHeight 기반으로 뷰포트를 확장하여 긴 캡처 수행
 * @param {import('puppeteer-core').Page} page
 * @param {import('puppeteer-core').ElementHandle} elementHandle
 * @param {Object} opts
 * @param {boolean} [opts.omitBackground=false]
 * @returns {Promise<Buffer>}
 */
async function captureLongElement(page, elementHandle, { omitBackground = false }) {
  const fullHeight = await elementHandle.evaluate((el) => {
    const rect = el.getBoundingClientRect();
    const scrollH = el.scrollHeight || 0;
    return Math.max(Math.ceil(rect.height), Math.ceil(scrollH));
  });

  const targetHeight = Math.min(fullHeight + 120, MAX_VIEWPORT_HEIGHT);
  const vp = page.viewport() || { width: 1080, height: 1920, deviceScaleFactor: 2 };
  const next = { ...vp, height: Math.max(vp.height, targetHeight) };
  await page.setViewport(next);

  await elementHandle.scrollIntoViewIfNeeded?.().catch(() => {});

  return await elementHandle.screenshot({
    type: 'png',
    omitBackground,
    captureBeyondViewport: true,
  });
}

/**
 * capture_mode에 따라 적절한 캡처 수행 (element / long / full_page)
 * @param {import('puppeteer-core').Page} page
 * @param {Object} options
 * @param {string} [options.capture_mode='full_page'] - element | long | full_page
 * @param {string} [options.selector=''] - CSS 셀렉터
 * @param {string} [options.style_mode=''] - CLEAN | FONT_UP | HIGHLIGHT | ZOOM
 * @param {Object} [options.style_args={}] - 스타일 추가 인자
 * @param {boolean} [options.omitBackground=false] - 투명 배경 여부
 * @returns {Promise<Buffer>} PNG 버퍼
 */
async function captureWithMode(page, options) {
  const {
    capture_mode = 'full_page',
    selector = '',
    style_mode = '',
    style_args = {},
    omitBackground = false,
  } = options;

  await applyCommonCleanup(page);
  if (style_mode && selector) {
    await applyStyleMode(page, { style_mode, selector, style_args });
  }

  if (capture_mode === 'element') {
    if (!selector) throw new Error('capture_mode=element requires selector');
    const el = await page.$(selector);
    if (!el) throw new Error(`Selector not found: ${selector}`);
    await el.scrollIntoViewIfNeeded?.().catch(() => {});
    return await el.screenshot({ type: 'png', omitBackground, captureBeyondViewport: true });
  }

  if (capture_mode === 'long') {
    if (selector) {
      const el = await page.$(selector);
      if (!el) throw new Error(`Selector not found for long capture: ${selector}`);
      return await captureLongElement(page, el, { omitBackground });
    }
    return await page.screenshot({ type: 'png', fullPage: true, omitBackground });
  }

  // full_page (default)
  return await page.screenshot({ type: 'png', fullPage: false, omitBackground });
}

/**
 * 기존 프리셋 기반 캡처 (v1 하위 호환)
 * @param {Object} params
 * @param {string} params.capture_id - 프리셋 ID (presets.js에서 매핑)
 * @param {Object} [params.capture_params] - 추가 파라미터
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

    // capture_params에 style_mode/capture_mode가 있으면 새 로직 위임
    if (capture_params?.capture_mode || capture_params?.style_mode) {
      const buf = await captureWithMode(page, {
        capture_mode: capture_params.capture_mode || 'full_page',
        selector: capture_params.selector || '',
        style_mode: capture_params.style_mode || '',
        style_args: capture_params.style_args || {},
        omitBackground: capture_params.omitBackground || false,
      });
      const skipResize = capture_params.capture_mode === 'element'
        || capture_params.capture_mode === 'long';
      const processedBuffer = await processImage(buf, { skipResize });
      const url = await uploadCapture(processedBuffer, capture_id);
      const timestamp = new Date().toISOString();
      return {
        url,
        capture_id,
        timestamp,
        dimensions: skipResize
          ? { width: 'original', height: 'original' }
          : { width: TARGET_WIDTH, height: TARGET_HEIGHT },
      };
    }

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

/**
 * 새 v2 캡처 (URL 직접 지정 + style_mode + capture_mode)
 * @param {Object} params
 * @param {string} params.url - 캡처 대상 URL
 * @param {string} [params.job_id] - 저장 경로용 Job ID
 * @param {string} [params.filename='capture.png'] - 저장 파일명
 * @param {string} [params.capture_mode='full_page'] - element | long | full_page
 * @param {string} [params.selector=''] - CSS 셀렉터
 * @param {string} [params.style_mode=''] - CLEAN | FONT_UP | HIGHLIGHT | ZOOM
 * @param {Object} [params.style_args={}] - 스타일 추가 인자
 * @param {boolean} [params.omitBackground=false] - 투명 배경 여부
 * @param {Object} [params.viewport] - 커스텀 뷰포트 {w, h}
 * @returns {Promise<Object>} 캡처 결과
 */
async function captureAdvanced({
  url,
  job_id,
  filename = 'capture.png',
  capture_mode = 'full_page',
  selector = '',
  style_mode = '',
  style_args = {},
  omitBackground = false,
  viewport,
}) {
  if (!url) {
    throw new Error('url is required for captureAdvanced');
  }

  const vw = viewport?.w || TARGET_WIDTH;
  const vh = viewport?.h || TARGET_HEIGHT;

  const browser = await getBrowser();
  const page = await browser.newPage();

  try {
    await page.setViewport({ width: vw, height: vh });
    await page.goto(url, {
      waitUntil: 'networkidle2',
      timeout: 30000,
    });

    // 동적 콘텐츠 렌더링 대기
    await page.evaluate(() => new Promise((resolve) => setTimeout(resolve, 2000)));

    const rawBuf = await captureWithMode(page, {
      capture_mode,
      selector,
      style_mode,
      style_args,
      omitBackground,
    });

    // element/long은 원본 비율 유지, full_page는 리사이즈 적용
    const skipResize = capture_mode === 'element' || capture_mode === 'long';
    const buf = await processImage(rawBuf, { skipResize });

    const uploadUrl = await uploadCapture(buf, 'advanced', { job_id, filename });
    const timestamp = new Date().toISOString();

    return {
      url: uploadUrl,
      capture_mode,
      style_mode: style_mode || 'none',
      selector: selector || 'none',
      timestamp,
      bytes: buf.length,
    };
  } finally {
    await page.close();
  }
}

module.exports = { capturePreset, captureAdvanced };
