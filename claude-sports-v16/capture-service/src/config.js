'use strict';

const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(__dirname, '..', '.env') });

/**
 * 환경변수 기반 설정 (IP 하드코딩 금지 준수)
 * @type {Object}
 */
const config = {
  port: parseInt(process.env.CAPTURE_PORT, 10) || 3100,
  captureBaseUrl: process.env.CAPTURE_BASE_URL || 'https://scoredata.org',
  chromiumPath: process.env.CHROMIUM_PATH || '/usr/bin/chromium',

  minio: {
    endPoint: process.env.MINIO_ENDPOINT || '127.0.0.1',
    port: parseInt(process.env.MINIO_PORT, 10) || 9000,
    useSSL: process.env.MINIO_USE_SSL === 'true',
    accessKey: process.env.MINIO_ACCESS_KEY || '',
    secretKey: process.env.MINIO_SECRET_KEY || '',
    bucket: process.env.MINIO_BUCKET || 'captures',
    publicHost: process.env.MINIO_PUBLIC_HOST || '127.0.0.1',
  },
};

module.exports = config;
