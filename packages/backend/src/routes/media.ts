import { FastifyInstance } from 'fastify';
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { config } from '../config';
import { logger } from '../utils/logger';
import crypto from 'crypto';

const ALLOWED_HOSTS = [process.env.VPS_HOST || '127.0.0.1'];

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

  // Generate images via kie.ai
  app.post('/api/media/generate-image', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    if (!config.kieai.apiKey) {
      return reply.status(501).send({ success: false, message: 'KIEAI_API_KEY not configured' });
    }

    const { prompt, count = 1, aspect_ratio, ref_subject, ref_scene, ref_style } = request.body as {
      prompt: string;
      count?: number;
      aspect_ratio?: '9:16' | '16:9';
      ref_subject?: string;
      ref_scene?: string;
      ref_style?: string;
    };

    if (!prompt?.trim()) {
      return reply.status(400).send({ success: false, message: 'prompt is required' });
    }

    const generateCount = Math.min(Math.max(count, 1), 3);
    const results: string[] = [];

    for (let i = 0; i < generateCount; i++) {
      try {
        // Create task
        const taskBody: Record<string, unknown> = {
          model: 'google/nano-banana-pro',
          input: {
            prompt: prompt.trim(),
            ...(aspect_ratio ? { aspect_ratio } : {}),
            ...(ref_subject ? { subject_image_url: ref_subject } : {}),
            ...(ref_scene ? { scene_image_url: ref_scene } : {}),
            ...(ref_style ? { style_image_url: ref_style } : {}),
          },
        };

        const createRes = await fetch(`${config.kieai.baseUrl}/jobs/createTask`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${config.kieai.apiKey}`,
          },
          body: JSON.stringify(taskBody),
        });

        if (!createRes.ok) {
          const errText = await createRes.text().catch(() => '');
          logger.error({ status: createRes.status, body: errText }, 'kie.ai createTask failed');
          continue;
        }

        const createData = await createRes.json() as { data?: { taskId?: string } };
        const taskId = createData.data?.taskId;
        if (!taskId) {
          logger.error({ createData }, 'kie.ai no taskId returned');
          continue;
        }

        // Poll for result (max 60s, 3s interval)
        let imageUrl: string | null = null;
        for (let attempt = 0; attempt < 20; attempt++) {
          await new Promise(r => setTimeout(r, 3000));

          const pollRes = await fetch(
            `${config.kieai.baseUrl}/jobs/recordInfo?taskId=${taskId}`,
            { headers: { Authorization: `Bearer ${config.kieai.apiKey}` } }
          );

          if (!pollRes.ok) continue;

          const pollData = await pollRes.json() as {
            data?: { status?: string; output?: { image_url?: string } };
          };

          if (pollData.data?.status === 'completed' && pollData.data.output?.image_url) {
            imageUrl = pollData.data.output.image_url;
            break;
          }
          if (pollData.data?.status === 'failed') {
            logger.error({ taskId, pollData }, 'kie.ai task failed');
            break;
          }
        }

        if (imageUrl) {
          results.push(imageUrl);
          logger.info({ taskId, imageUrl }, 'kie.ai image generated');
        }
      } catch (err) {
        logger.error({ error: err }, 'kie.ai generation error');
      }
    }

    return { success: true, data: { images: results } };
  });

  // Save external image to MinIO (download → re-upload)
  app.post('/api/media/save-external', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const { url } = request.body as { url: string };
    if (!url) {
      return reply.status(400).send({ success: false, message: 'url is required' });
    }

    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);

      const buf = Buffer.from(await res.arrayBuffer());
      const contentType = res.headers.get('content-type') || 'image/png';
      const ext = contentType.includes('jpeg') ? 'jpg' : contentType.includes('webp') ? 'webp' : 'png';
      const key = `generated/${Date.now()}-${crypto.randomBytes(6).toString('hex')}.${ext}`;

      await s3.send(new PutObjectCommand({
        Bucket: config.minio.bucket,
        Key: key,
        Body: buf,
        ContentType: contentType,
      }));

      const savedUrl = `${config.minio.endpoint}/${config.minio.bucket}/${key}`;
      logger.info({ key, size: buf.length }, 'External image saved to MinIO');

      return { success: true, data: { url: savedUrl } };
    } catch (err) {
      logger.error({ url, error: err }, 'Failed to save external image');
      return reply.status(500).send({ success: false, message: 'Failed to save image' });
    }
  });

  // Analyze image via Claude Vision
  app.post('/api/media/analyze-image', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    if (!config.claude.apiKey) {
      return reply.status(501).send({ success: false, message: 'CLAUDE_API_KEY not configured' });
    }

    const { imageUrl } = request.body as { imageUrl: string };
    if (!imageUrl) {
      return reply.status(400).send({ success: false, message: 'imageUrl is required' });
    }

    try {
      const res = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': config.claude.apiKey,
          'anthropic-version': '2023-06-01',
        },
        body: JSON.stringify({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 300,
          messages: [{
            role: 'user',
            content: [
              {
                type: 'image',
                source: { type: 'url', url: imageUrl },
              },
              {
                type: 'text',
                text: 'Describe this image in 2-3 sentences for a short-form video script. Focus on the subject, scene, mood, and visual style. Reply in Korean.',
              },
            ],
          }],
        }),
      });

      if (!res.ok) {
        const errText = await res.text().catch(() => '');
        logger.error({ status: res.status, body: errText }, 'Claude Vision API failed');
        return reply.status(502).send({ success: false, message: 'Claude Vision API failed' });
      }

      const data = await res.json() as {
        content?: { type: string; text?: string }[];
      };
      const analysis = data.content?.find(c => c.type === 'text')?.text || '';

      return { success: true, data: { analysis } };
    } catch (err) {
      logger.error({ error: err }, 'Claude Vision error');
      return reply.status(500).send({ success: false, message: 'Image analysis failed' });
    }
  });
}
