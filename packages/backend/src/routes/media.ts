import { FastifyInstance } from 'fastify';
import { logger } from '../utils/logger';

const ALLOWED_HOSTS = ['76.13.182.180'];

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
}
