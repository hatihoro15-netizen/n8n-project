import { FastifyInstance } from 'fastify';
import { ProductionStatus } from '@prisma/client';
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
    if (status) {
      where.status = status;
    } else {
      // 기본적으로 archived 제외
      where.status = { not: 'archived' };
    }

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
        data: { status: 'started', startedAt: new Date() },
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

  // AO Pipeline: create production + trigger webhook (with workflow selection)
  app.post('/api/productions/ao', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const body = request.body as {
      workflowId: string;
      prompt_p1?: string;
      topic?: string;
      keywords?: string;
      category?: string;
      production_mode?: 'ai_video' | 'slideshow';
      clip_duration?: number;
      slide_duration?: number;
      files?: {
        type: 'image' | 'video';
        url: string;
        analysis?: string;
        vision_analysis?: string;
        use_directly?: boolean;
        use_mode?: 'direct' | 'generate' | 'analysis_only';
        auto_prompt?: string;
      }[];
      ref_files?: {
        type: 'image';
        url: string;
        analysis?: string;
        vision_analysis?: string;
        use_directly?: boolean;
        use_mode?: 'direct' | 'generate' | 'analysis_only';
        auto_prompt?: string;
      }[];
      clips?: {
        image_url: string;
        vision_analysis?: string;
        scene_prompt?: string;
        include_audio?: boolean;
      }[];
    };

    if (!body.workflowId) {
      return reply.status(400).send({ success: false, message: 'workflowId is required' });
    }

    // Find selected workflow
    const workflow = await prisma.workflow.findUnique({
      where: { id: body.workflowId },
      include: { channel: true },
    });

    if (!workflow) {
      return reply.status(404).send({ success: false, message: '워크플로우를 찾을 수 없습니다.' });
    }
    if (!workflow.webhookPath) {
      return reply.status(400).send({ success: false, message: '웹훅 경로가 설정되지 않은 워크플로우입니다.' });
    }

    // Create production record
    const production = await prisma.production.create({
      data: {
        workflowId: workflow.id,
        channelId: workflow.channelId,
        topic: body.topic || body.prompt_p1?.slice(0, 100) || 'AO Production',
        status: 'pending',
      },
      include: { workflow: true, channel: true },
    });

    // Trigger n8n webhook with productionId + full payload
    try {
      await n8nClient.triggerWebhook(workflow.webhookPath, {
        productionId: production.id,
        prompt_p1: body.prompt_p1,
        topic: body.topic,
        keywords: body.keywords,
        category: body.category,
        production_mode: body.production_mode || 'ai_video',
        clip_duration: body.clip_duration,
        slide_duration: body.slide_duration,
        files: body.files,
        ref_files: body.ref_files,
        clips: body.clips,
      });

      await prisma.production.update({
        where: { id: production.id },
        data: { status: 'started', startedAt: new Date() },
      });

      logger.info({ productionId: production.id, workflowId: workflow.id }, 'AO production triggered');
    } catch (error) {
      await prisma.production.update({
        where: { id: production.id },
        data: {
          status: 'failed',
          errorMessage: error instanceof Error ? error.message : 'Webhook trigger failed',
        },
      });
      logger.error({ productionId: production.id, error }, 'AO webhook trigger failed');
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
            status: 'started',
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

  // Abort/update production status
  app.patch('/api/productions/:id', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const { id } = request.params as { id: string };
    const { status, errorMessage } = request.body as {
      status: string;
      errorMessage?: string;
    };

    const validStatuses = [...Object.values(ProductionStatus), 'restore'];
    if (!validStatuses.includes(status as string)) {
      return reply.status(400).send({ success: false, message: `유효하지 않은 상태: ${status}` });
    }

    const production = await prisma.production.findUnique({
      where: { id },
    });

    if (!production) {
      return reply.status(404).send({ success: false, message: '제작 건을 찾을 수 없습니다.' });
    }

    // 보관 처리
    if (status === 'archived') {
      if (!['completed', 'failed', 'paused'].includes(production.status)) {
        return reply.status(400).send({ success: false, message: '완료/실패/정지 상태만 보관할 수 있습니다.' });
      }
      const updated = await prisma.production.update({
        where: { id },
        data: {
          previousStatus: production.status,
          status: 'archived' as ProductionStatus,
        },
        include: { workflow: true, channel: true },
      });
      logger.info({ productionId: id, previousStatus: production.status }, 'Production archived');
      return { success: true, data: updated };
    }

    // 복원 처리 (archived → 원래 상태)
    if (status === 'restore') {
      if (production.status !== 'archived') {
        return reply.status(400).send({ success: false, message: '보관된 제작 건만 복원할 수 있습니다.' });
      }
      const restoreStatus = (production.previousStatus || 'completed') as ProductionStatus;
      const updated = await prisma.production.update({
        where: { id },
        data: {
          status: restoreStatus,
          previousStatus: null,
        },
        include: { workflow: true, channel: true },
      });
      logger.info({ productionId: id, restoredTo: restoreStatus }, 'Production restored');
      return { success: true, data: updated };
    }

    if (['completed', 'failed', 'paused', 'archived'].includes(production.status) && status !== 'paused') {
      return reply.status(400).send({ success: false, message: '이미 완료/실패/정지/보관된 제작 건입니다.' });
    }

    // 정지 요청 시 n8n 실행도 중단
    if (status === 'paused' && production.n8nExecutionId) {
      try {
        await n8nClient.stopExecution(production.n8nExecutionId);
        logger.info({ productionId: id, executionId: production.n8nExecutionId }, 'n8n execution stopped');
      } catch (err) {
        logger.warn({ productionId: id, error: err }, 'Failed to stop n8n execution (may already be finished)');
      }
    }

    const newStatus = status as ProductionStatus;
    const updated = await prisma.production.update({
      where: { id },
      data: {
        status: newStatus,
        errorMessage: errorMessage || undefined,
        completedAt: ['completed', 'failed'].includes(newStatus) ? new Date() : undefined,
      },
      include: { workflow: true, channel: true },
    });

    logger.info({ productionId: id, status, errorMessage }, 'Production status updated manually');

    return { success: true, data: updated };
  });

  // Delete production (only non-in-progress)
  const IN_PROGRESS_STATUSES = ['started', 'script_ready', 'tts_ready', 'images_ready', 'videos_ready', 'rendering', 'uploading'];

  app.delete('/api/productions/:id', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const { id } = request.params as { id: string };

    const production = await prisma.production.findUnique({ where: { id } });

    if (!production) {
      return reply.status(404).send({ success: false, message: '제작 건을 찾을 수 없습니다.' });
    }

    if (IN_PROGRESS_STATUSES.includes(production.status)) {
      return reply.status(400).send({
        success: false,
        message: '진행중인 제작은 삭제할 수 없습니다. 먼저 중단하세요.',
      });
    }

    await prisma.production.delete({ where: { id } });
    logger.info({ productionId: id, status: production.status }, 'Production deleted');

    return { success: true, message: '제작이 삭제되었습니다.' };
  });

  // Status progression order (higher = more advanced)
  const STATUS_ORDER: Record<string, number> = {
    pending: 0,
    started: 1,
    script_ready: 2,
    tts_ready: 3,
    images_ready: 4,
    videos_ready: 5,
    rendering: 6,
    uploading: 7,
    completed: 8,
    failed: 9,
    paused: -1, // special: handled via exception
    archived: -2, // special: handled via exception
  };

  // n8n callback endpoint (no auth - called by n8n)
  app.post('/api/productions/callback', async (request, reply) => {
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
      executionId,
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
      executionId?: string;
    };

    // Fetch current production (status + assets)
    const existingProd = await prisma.production.findUnique({
      where: { id: productionId },
      select: { status: true, assets: true },
    });

    if (!existingProd) {
      return reply.status(404).send({ success: false, message: 'Production not found' });
    }

    // If production is paused or archived, ignore all callbacks
    if (existingProd.status === 'paused' || existingProd.status === 'archived') {
      logger.info(
        { productionId, incomingStatus: status, currentStatus: existingProd.status },
        `Callback ignored: production is ${existingProd.status}`
      );
      return { success: true, skipped: true, message: `Production is ${existingProd.status}` };
    }

    // Regression guard: skip if incoming status is behind current progress
    // Exception: 'failed' can always override (error at any stage)
    const currentOrder = STATUS_ORDER[existingProd.status] ?? -1;
    const incomingOrder = STATUS_ORDER[status] ?? -1;

    if (status !== 'failed' && incomingOrder <= currentOrder) {
      logger.info(
        { productionId, currentStatus: existingProd.status, incomingStatus: status },
        'Callback ignored: status regression'
      );
      return { success: true, skipped: true, message: `Current status (${existingProd.status}) is already ahead of ${status}` };
    }

    // Build assets object, merging with existing
    const mergedAssets: Record<string, unknown> = {
      ...((existingProd.assets as Record<string, unknown>) || {}),
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
    if (executionId) data.n8nExecutionId = executionId;
    if (status === 'completed' || status === 'failed') data.completedAt = new Date();

    const production = await prisma.production.update({
      where: { id: productionId },
      data,
    });

    logger.info({ productionId, status }, 'Production callback received');

    // TODO: broadcast via WebSocket to connected clients

    return { success: true, data: production };
  });

  // Stop production — pause DB + stop n8n execution
  app.post('/api/productions/:id/stop', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const { id } = request.params as { id: string };

    const production = await prisma.production.findUnique({ where: { id } });

    if (!production) {
      return reply.status(404).send({ success: false, message: '제작 건을 찾을 수 없습니다.' });
    }

    if (['completed', 'failed', 'paused', 'archived'].includes(production.status)) {
      return reply.status(400).send({ success: false, message: '이미 완료/실패/정지/보관된 제작 건입니다.' });
    }

    // n8n 실행 중단
    if (production.n8nExecutionId) {
      try {
        await n8nClient.stopExecution(production.n8nExecutionId);
        logger.info({ productionId: id, executionId: production.n8nExecutionId }, 'n8n execution stopped');
      } catch (err) {
        logger.warn({ productionId: id, error: err }, 'Failed to stop n8n execution (may already be finished)');
      }
    }

    const updated = await prisma.production.update({
      where: { id },
      data: { status: 'paused' },
      include: { workflow: true, channel: true },
    });

    logger.info({ productionId: id }, 'Production stopped and paused');

    return { success: true, data: updated };
  });

  // Retry failed/paused production via n8n execution retry API
  app.post('/api/productions/:id/retry', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const { id } = request.params as { id: string };

    const production = await prisma.production.findUnique({
      where: { id },
      include: { workflow: true },
    });

    if (!production) {
      return reply.status(404).send({ success: false, message: '제작 건을 찾을 수 없습니다.' });
    }

    if (production.status !== 'failed' && production.status !== 'paused') {
      return reply.status(400).send({ success: false, message: '실패하거나 정지된 제작 건만 재시도할 수 있습니다.' });
    }

    if (!production.n8nExecutionId) {
      return reply.status(400).send({ success: false, message: 'n8n 실행 ID가 없어 재시도할 수 없습니다. "처음부터 다시 만들기"를 사용하세요.' });
    }

    try {
      const retryResult = await n8nClient.retryExecution(production.n8nExecutionId);

      // Reset production status to started for fresh tracking
      await prisma.production.update({
        where: { id },
        data: {
          status: 'started',
          errorMessage: null,
          completedAt: null,
          n8nExecutionId: (retryResult as { data?: { id?: string } })?.data?.id || production.n8nExecutionId,
        },
      });

      const updated = await prisma.production.findUnique({
        where: { id },
        include: { workflow: true, channel: true },
      });

      logger.info({ productionId: id, executionId: production.n8nExecutionId }, 'Production retry triggered');

      return { success: true, data: updated };
    } catch (error) {
      logger.error({ productionId: id, error }, 'Failed to retry production');
      return reply.status(500).send({
        success: false,
        message: error instanceof Error ? error.message : 'n8n 재시도 실패',
      });
    }
  });
}
