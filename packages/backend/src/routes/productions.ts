import { FastifyInstance } from 'fastify';
import { ProductionStatus } from '@prisma/client';
import { prisma } from '../utils/prisma';
import { n8nClient } from '../utils/n8n-client';
import { logger } from '../utils/logger';
import { config } from '../config';

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

  // Lightweight status poll (for real-time progress bar)
  app.get('/api/productions/:id/status', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const { id } = request.params as { id: string };
    const production = await prisma.production.findUnique({
      where: { id },
      select: { status: true, errorMessage: true, assets: true },
    });
    if (!production) {
      return reply.status(404).send({ success: false, message: 'Not found' });
    }
    const assets = (production.assets || {}) as Record<string, unknown>;
    return {
      success: true,
      data: {
        status: production.status,
        errorMessage: production.errorMessage,
        videoUrl: assets.videoUrl || assets.video_url || null,
        thumbnailUrl: assets.thumbnailUrl || assets.thumbnail_url || null,
      },
    };
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
      aspect_ratio?: '9:16' | '16:9';
      production_mode?: 'ai_video' | 'slideshow';
      has_images?: boolean;
      slide_duration?: number;
      generated_images?: string[];
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
      duration_sec?: number;
      engine_type?: string;
      strict_mode?: boolean;
      image_order?: 'auto' | 'sequential';
      narration_text?: string;
      narration_style?: string;
      narration_tone?: string;
      bgm_mode?: 'ai_auto' | 'uploaded' | 'none';
      sfx_mode?: 'ai_auto' | 'uploaded' | 'combined' | 'none';
      bgm_url?: string;
      sfx_url?: string;
    };

    if (!body.workflowId) {
      return reply.status(400).send({ success: false, message: 'workflowId is required' });
    }
    if (!body.prompt_p1?.trim()) {
      return reply.status(400).send({ success: false, message: 'prompt_p1 is required' });
    }
    const ALLOWED_ENGINES = ['character_story', 'core_message', 'live_promo', 'meme', 'action_sports'];
    if (body.engine_type && !ALLOWED_ENGINES.includes(body.engine_type)) {
      return reply.status(400).send({ success: false, message: `engine_type must be one of: ${ALLOWED_ENGINES.join(', ')}` });
    }
    const ALLOWED_NARRATION_STYLES = ['설명형', '스토리형', '광고형', '감성형'];
    if (body.narration_style && !ALLOWED_NARRATION_STYLES.includes(body.narration_style)) {
      return reply.status(400).send({ success: false, message: `narration_style must be one of: ${ALLOWED_NARRATION_STYLES.join(', ')}` });
    }
    const ALLOWED_NARRATION_TONES = ['차분하게', '흥분되게', '유머러스하게', '긴박하게'];
    if (body.narration_tone && !ALLOWED_NARRATION_TONES.includes(body.narration_tone)) {
      return reply.status(400).send({ success: false, message: `narration_tone must be one of: ${ALLOWED_NARRATION_TONES.join(', ')}` });
    }
    const ALLOWED_BGM_MODES = ['ai_auto', 'uploaded', 'none'];
    if (body.bgm_mode && !ALLOWED_BGM_MODES.includes(body.bgm_mode)) {
      return reply.status(400).send({ success: false, message: `bgm_mode must be one of: ${ALLOWED_BGM_MODES.join(', ')}` });
    }
    const ALLOWED_SFX_MODES = ['ai_auto', 'uploaded', 'combined', 'none'];
    if (body.sfx_mode && !ALLOWED_SFX_MODES.includes(body.sfx_mode)) {
      return reply.status(400).send({ success: false, message: `sfx_mode must be one of: ${ALLOWED_SFX_MODES.join(', ')}` });
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

    // Create production record with params snapshot
    const production = await prisma.production.create({
      data: {
        workflowId: workflow.id,
        channelId: workflow.channelId,
        topic: body.topic || body.prompt_p1?.slice(0, 100) || 'AO Production',
        status: 'pending',
        assets: {
          params: {
            prompt_p1: body.prompt_p1,
            aspect_ratio: body.aspect_ratio || '9:16',
            production_mode: body.production_mode || 'ai_video',
            engine_type: body.engine_type || 'core_message',
            strict_mode: body.strict_mode ?? false,
            duration_sec: body.duration_sec ?? 0,
            image_order: body.image_order || 'auto',
            has_images: body.has_images ?? false,
            narration_text: body.narration_text,
            narration_style: body.narration_style || '설명형',
            narration_tone: body.narration_tone || '차분하게',
            bgm_mode: body.bgm_mode || 'ai_auto',
            sfx_mode: body.sfx_mode || 'ai_auto',
          },
        },
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
        aspect_ratio: body.aspect_ratio || '9:16',
        production_mode: body.production_mode || 'ai_video',
        engine_type: body.engine_type || 'core_message',
        strict_mode: body.strict_mode || false,
        duration_sec: body.duration_sec ?? 0,
        image_order: body.image_order || 'auto',
        has_images: body.has_images,
        slide_duration: body.slide_duration,
        generated_images: body.generated_images,
        files: body.files,
        ref_files: body.ref_files,
        clips: body.clips,
        narration_text: body.narration_text,
        narration_style: body.narration_style || '설명형',
        narration_tone: body.narration_tone || '차분하게',
        bgm_mode: body.bgm_mode || 'ai_auto',
        sfx_mode: body.sfx_mode || 'ai_auto',
        bgm_url: body.bgm_url,
        sfx_url: body.sfx_url,
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
      const errMsg = error instanceof Error ? error.message : String(error);
      logger.error({ productionId: production.id, error: errMsg }, 'AO webhook trigger failed');
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
  // Prisma enum 기준 순서 + n8n Worker가 보내는 status도 포함 (매핑 전 regression guard용)
  const STATUS_ORDER: Record<string, number> = {
    pending: 0,
    started: 1,
    processing: 2,     // n8n Worker → skip (매핑: no-op)
    script_ready: 3,
    tts_ready: 4,
    images_ready: 5,
    generated: 6,       // n8n Worker → videos_ready
    videos_ready: 7,
    rendering: 8,
    uploading: 9,
    uploaded: 10,       // n8n Worker → completed
    completed: 11,
    failed: 12,
    paused: -1,
    archived: -2,
  };

  // n8n callback endpoint (no auth - called by n8n)
  app.post('/api/productions/callback', async (request, reply) => {
    logger.info({ callbackBody: request.body }, 'Callback raw body');
    const {
      productionId,
      status,
      title,
      assets,
      videoUrl,
      renderedVideoUrl,
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
      renderedVideoUrl?: string;
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

    // Build assets object, merging with existing (preserve params from creation)
    const existingAssets = (existingProd.assets as Record<string, unknown>) || {};
    const mergedAssets: Record<string, unknown> = {
      ...existingAssets,
      ...(assets || {}),
    };
    // Ensure params saved at creation are never overwritten by callback
    if (existingAssets.params) {
      mergedAssets.params = existingAssets.params;
    }
    const finalVideoUrl = videoUrl || renderedVideoUrl;
    if (finalVideoUrl) mergedAssets.videoUrl = finalVideoUrl;
    if (thumbnailUrl) mergedAssets.thumbnailUrl = thumbnailUrl;
    if (script) mergedAssets.script = script;

    // n8n Worker status → Prisma enum 매핑 (스키마 변경 없이 처리)
    // processing → skip (이미 started 상태), generated → videos_ready, uploaded → completed
    if (status === 'processing') {
      logger.info({ productionId, status }, 'Callback: processing status skipped (already started)');
      return { success: true, skipped: true, message: 'processing mapped to started (no-op)' };
    }
    const STATUS_MAP: Record<string, string> = {
      generated: 'videos_ready',
      uploaded: 'completed',
    };
    const finalStatus = STATUS_MAP[status] || status;

    const data: Record<string, unknown> = { status: finalStatus, assets: mergedAssets };
    if (title) data.title = title;
    if (youtubeVideoId) data.youtubeVideoId = youtubeVideoId;
    if (youtubeUrl) data.youtubeUrl = youtubeUrl;
    if (errorMessage) data.errorMessage = errorMessage;
    if (executionId) data.n8nExecutionId = executionId;
    if (finalStatus === 'completed' || finalStatus === 'failed') data.completedAt = new Date();

    const production = await prisma.production.update({
      where: { id: productionId },
      data,
    });

    logger.info({ productionId, status: finalStatus, originalStatus: status }, 'Production callback received');

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

  // AI Suggest Prompt (Claude API)
  app.post('/api/productions/suggest-prompt', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    if (!config.claude.apiKey) {
      return reply.status(501).send({ success: false, message: 'CLAUDE_API_KEY not configured' });
    }

    const { prompt_p1, narration_text, duration_sec } = request.body as {
      prompt_p1: string;
      narration_text?: string;
      duration_sec?: number;
    };

    if (!prompt_p1?.trim()) {
      return reply.status(400).send({ success: false, message: 'prompt_p1 is required' });
    }

    const durationHint = duration_sec && duration_sec > 0 ? `영상 길이: ${duration_sec}초` : '영상 길이: AI 자동 판단';
    const narrationHint = narration_text?.trim() ? `나레이션 스크립트:\n${narration_text.trim()}` : '';

    const systemPrompt = `당신은 숏폼 영상 제작 전문가입니다. 사용자의 영상 기획 의도를 바탕으로 두 가지를 생성합니다:

1. **한글 연출 스크립트**: 장면 구성, 카메라 워크, 분위기, 전환 효과 등을 포함한 상세 연출 지시서 (제작팀용)
2. **영문 Kling 프롬프트**: Kling AI 영상 생성 모델에 최적화된 영문 프롬프트 (cinematic, camera movement, lighting 등 키워드 포함)

반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
{"korean": "한글 연출 스크립트", "english": "English Kling prompt"}`;

    const userMessage = [
      `영상 기획 의도: ${prompt_p1.trim()}`,
      durationHint,
      narrationHint,
    ].filter(Boolean).join('\n\n');

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
          max_tokens: 1500,
          system: systemPrompt,
          messages: [{ role: 'user', content: userMessage }],
        }),
      });

      if (!res.ok) {
        const errText = await res.text().catch(() => '');
        logger.error({ status: res.status, body: errText }, 'Claude suggest-prompt API failed');
        return reply.status(502).send({ success: false, message: 'Claude API failed' });
      }

      const data = await res.json() as { content: { type: string; text: string }[] };
      const text = data.content?.[0]?.text || '';

      // 마크다운 코드블록 제거 후 JSON 파싱
      const cleaned = text.replace(/```(?:json)?\s*/g, '').replace(/```\s*$/g, '').trim();
      try {
        const parsed = JSON.parse(cleaned);
        return { success: true, data: { korean: parsed.korean || '', english: parsed.english || '' } };
      } catch {
        // JSON 파싱 실패 시 전체 텍스트를 korean으로 반환
        logger.warn({ text }, 'suggest-prompt: Claude response not valid JSON');
        return { success: true, data: { korean: text, english: '' } };
      }
    } catch (error) {
      logger.error({ error }, 'suggest-prompt failed');
      return reply.status(500).send({
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });
}
