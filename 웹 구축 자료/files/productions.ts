import { FastifyInstance } from 'fastify';
import { prisma } from '../utils/prisma';
import { n8nClient } from '../utils/n8n-client';
import { logger } from '../utils/logger';

export async function productionRoutes(app: FastifyInstance) {
  // List productions with filters
  app.get('/api/productions', {
    preHandler: [app.authenticate],
  }, async (request) => {
    const { channelId, status, page = '1', limit = '20' } = request.query as {
      channelId?: string;
      status?: string;
      page?: string;
      limit?: string;
    };

    const where: Record<string, unknown> = {};
    if (channelId) where.channelId = channelId;
    if (status) where.status = status;

    const pageNum = parseInt(page, 10);
    const limitNum = parseInt(limit, 10);

    const [productions, total] = await Promise.all([
      prisma.production.findMany({
        where,
        include: {
          workflow: true,
          channel: true,
        },
        orderBy: { createdAt: 'desc' },
        skip: (pageNum - 1) * limitNum,
        take: limitNum,
      }),
      prisma.production.count({ where }),
    ]);

    return {
      success: true,
      data: productions,
      pagination: {
        page: pageNum,
        limit: limitNum,
        total,
        totalPages: Math.ceil(total / limitNum),
      },
    };
  });

  // Get single production
  app.get('/api/productions/:id', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const { id } = request.params as { id: string };

    const production = await prisma.production.findUnique({
      where: { id },
      include: {
        workflow: { include: { channel: true } },
        channel: true,
      },
    });

    if (!production) {
      return reply.status(404).send({ success: false, message: '제작 건을 찾을 수 없습니다.' });
    }

    return { success: true, data: production };
  });

  // Trigger new production
  app.post('/api/productions', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const { workflowId, topic } = request.body as {
      workflowId: string;
      topic?: string;
    };

    const workflow = await prisma.workflow.findUnique({
      where: { id: workflowId },
      include: { channel: true },
    });

    if (!workflow) {
      return reply.status(404).send({ success: false, message: '워크플로우를 찾을 수 없습니다.' });
    }

    if (!workflow.webhookPath) {
      return reply.status(400).send({ success: false, message: '웹훅 경로가 설정되지 않았습니다.' });
    }

    // Create production record
    const production = await prisma.production.create({
      data: {
        workflowId: workflow.id,
        channelId: workflow.channelId,
        topic,
        status: 'pending',
      },
      include: { workflow: true, channel: true },
    });

    // Trigger n8n webhook
    try {
      await n8nClient.triggerWebhook(workflow.webhookPath, {
        productionId: production.id,
        topic,
      });

      await prisma.production.update({
        where: { id: production.id },
        data: { status: 'triggered', startedAt: new Date() },
      });

      logger.info({ productionId: production.id, workflowId }, 'Production triggered');
    } catch (error) {
      await prisma.production.update({
        where: { id: production.id },
        data: {
          status: 'failed',
          errorMessage: error instanceof Error ? error.message : 'Webhook trigger failed',
        },
      });

      logger.error({ productionId: production.id, error }, 'Failed to trigger production');
    }

    const updated = await prisma.production.findUnique({
      where: { id: production.id },
      include: { workflow: true, channel: true },
    });

    return { success: true, data: updated };
  });

  // Batch trigger
  app.post('/api/productions/batch', {
    preHandler: [app.authenticate],
  }, async (request) => {
    const { items } = request.body as {
      items: { workflowId: string; topic?: string }[];
    };

    const results = [];
    for (const item of items) {
      try {
        const workflow = await prisma.workflow.findUnique({
          where: { id: item.workflowId },
        });

        if (!workflow?.webhookPath) {
          results.push({ workflowId: item.workflowId, success: false, error: 'No webhook path' });
          continue;
        }

        const production = await prisma.production.create({
          data: {
            workflowId: workflow.id,
            channelId: workflow.channelId,
            topic: item.topic,
            status: 'triggered',
            startedAt: new Date(),
          },
        });

        await n8nClient.triggerWebhook(workflow.webhookPath, {
          productionId: production.id,
          topic: item.topic,
        });

        results.push({ workflowId: item.workflowId, productionId: production.id, success: true });
      } catch (error) {
        results.push({
          workflowId: item.workflowId,
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    }

    return { success: true, data: results };
  });

  // n8n callback endpoint (no auth - called by n8n)
  app.post('/api/productions/callback', async (request) => {
    const {
      productionId,
      status,
      title,
      assets,
      videoUrl,
      thumbnailUrl,
      script,
      youtubeVideoId,
      youtubeUrl,
      errorMessage,
    } = request.body as {
      productionId: string;
      status: string;
      title?: string;
      assets?: Record<string, unknown>;
      videoUrl?: string;
      thumbnailUrl?: string;
      script?: string;
      youtubeVideoId?: string;
      youtubeUrl?: string;
      errorMessage?: string;
    };

    // Build assets object, merging explicit fields with passed assets
    const existingProd = await prisma.production.findUnique({
      where: { id: productionId },
      select: { assets: true },
    });

    const mergedAssets: Record<string, unknown> = {
      ...((existingProd?.assets as Record<string, unknown>) || {}),
      ...(assets || {}),
    };
    if (videoUrl) mergedAssets.videoUrl = videoUrl;
    if (thumbnailUrl) mergedAssets.thumbnailUrl = thumbnailUrl;
    if (script) mergedAssets.script = script;

    const data: Record<string, unknown> = { status, assets: mergedAssets };
    if (title) data.title = title;
    if (youtubeVideoId) data.youtubeVideoId = youtubeVideoId;
    if (youtubeUrl) data.youtubeUrl = youtubeUrl;
    if (errorMessage) data.errorMessage = errorMessage;
    if (status === 'completed' || status === 'failed') data.completedAt = new Date();

    const production = await prisma.production.update({
      where: { id: productionId },
      data,
    });

    logger.info({ productionId, status }, 'Production callback received');

    // TODO: broadcast via WebSocket to connected clients

    return { success: true, data: production };
  });
}
