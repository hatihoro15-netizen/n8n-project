import { FastifyInstance } from 'fastify';
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { config } from '../config';
import { logger } from '../utils/logger';
import crypto from 'crypto';

const ALLOWED_HOSTS = ['76.13.182.180'];

const s3 = new S3Client({
  endpoint: config.minio.endpoint,
  region: config.minio.region,
  credentials: {
    accessKeyId: config.minio.accessKey,
    secretAccessKey: config.minio.secretKey,
  },
  forcePathStyle: true,
});

export async function mediaRoutes(app: FastifyInstance) {
  // Proxy media from internal MinIO to avoid mixed content (HTTPS frontend → HTTP MinIO)
  app.get('/api/media/proxy', async (request, reply) => {
    const { url } = request.query as { url?: string };

    if (!url) {
      return reply.status(400).send({ success: false, message: 'url parameter required' });
    }

    // Validate allowed origin to prevent open proxy abuse
    let parsed: URL;
    try {
      parsed = new URL(url);
      if (!ALLOWED_HOSTS.includes(parsed.hostname)) {
        return reply.status(403).send({ success: false, message: 'URL not allowed' });
      }
    } catch {
      return reply.status(400).send({ success: false, message: 'Invalid URL' });
    }

    // Forward Range header for video seeking
    const headers: Record<string, string> = {};
    if (request.headers.range) {
      headers.Range = request.headers.range;
    }

    try {
      const upstream = await fetch(url, { headers });

      reply.status(upstream.status);

      // Pass through relevant headers
      const ct = upstream.headers.get('content-type');
      if (ct) reply.header('Content-Type', ct);

      const cl = upstream.headers.get('content-length');
      if (cl) reply.header('Content-Length', cl);

      const cr = upstream.headers.get('content-range');
      if (cr) reply.header('Content-Range', cr);

      reply.header('Accept-Ranges', 'bytes');
      reply.header('Cache-Control', 'public, max-age=86400');

      // Extract filename from URL path for Content-Disposition
      const filename = decodeURIComponent(parsed.pathname.split('/').pop() || 'download');
      reply.header('Content-Disposition', `inline; filename="${filename}"`);

      if (!upstream.body) {
        return reply.send(Buffer.alloc(0));
      }

      return reply.send(Buffer.from(await upstream.arrayBuffer()));
    } catch (error) {
      logger.error({ url, error }, 'Media proxy failed');
      return reply.status(502).send({ success: false, message: 'Failed to fetch media' });
    }
  });

  // Upload images to MinIO
  app.post('/api/media/upload', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
    const MAX_FILES = 4;

    const parts = request.parts();
    const uploaded: string[] = [];

    for await (const part of parts) {
      if (part.type !== 'file') continue;
      if (uploaded.length >= MAX_FILES) break;

      if (!ALLOWED_TYPES.includes(part.mimetype)) {
        return reply.status(400).send({
          success: false,
          message: `허용되지 않는 파일 형식: ${part.mimetype}`,
        });
      }

      const ext = part.filename?.split('.').pop() || 'jpg';
      const key = `uploads/${Date.now()}-${crypto.randomBytes(6).toString('hex')}.${ext}`;
      const buf = await part.toBuffer();

      await s3.send(new PutObjectCommand({
        Bucket: config.minio.bucket,
        Key: key,
        Body: buf,
        ContentType: part.mimetype,
      }));

      const url = `${config.minio.endpoint}/${config.minio.bucket}/${key}`;
      uploaded.push(url);
      logger.info({ key, size: buf.length }, 'Image uploaded to MinIO');
    }

    if (uploaded.length === 0) {
      return reply.status(400).send({ success: false, message: '파일이 첨부되지 않았습니다.' });
    }

    return { success: true, data: { urls: uploaded } };
  });
}
