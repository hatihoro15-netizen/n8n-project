'use strict';

const Minio = require('minio');
const config = require('./config');

/** @type {Minio.Client|null} */
let minioClient = null;

/**
 * MinIO 클라이언트 싱글턴 반환
 * @returns {Minio.Client}
 */
function getClient() {
  if (!minioClient) {
    minioClient = new Minio.Client({
      endPoint: config.minio.endPoint,
      port: config.minio.port,
      useSSL: config.minio.useSSL,
      accessKey: config.minio.accessKey,
      secretKey: config.minio.secretKey,
    });
  }
  return minioClient;
}

/**
 * 버킷 존재 확인 후 없으면 생성
 * @returns {Promise<void>}
 */
async function ensureBucket() {
  const client = getClient();
  const bucket = config.minio.bucket;
  const exists = await client.bucketExists(bucket);
  if (!exists) {
    await client.makeBucket(bucket, '');
  }
}

/**
 * PNG 이미지를 MinIO에 업로드하고 공개 URL 반환
 * 저장 경로: captures/{날짜}/{capture_id}_{timestamp}.png
 * @param {Buffer} imageBuffer - PNG 이미지 버퍼
 * @param {string} captureId - 프리셋 ID
 * @returns {Promise<string>} 공개 접근 URL
 */
async function uploadCapture(imageBuffer, captureId) {
  const client = getClient();
  const bucket = config.minio.bucket;
  const dateStr = new Date().toISOString().split('T')[0];
  const timestamp = Date.now();
  const objectName = `${dateStr}/${captureId}_${timestamp}.png`;

  await client.putObject(bucket, objectName, imageBuffer, imageBuffer.length, {
    'Content-Type': 'image/png',
  });

  const protocol = config.minio.useSSL ? 'https' : 'http';
  const host = config.minio.publicHost;
  const port = config.minio.port;
  const url = `${protocol}://${host}:${port}/${bucket}/${objectName}`;

  return url;
}

module.exports = { ensureBucket, uploadCapture };
