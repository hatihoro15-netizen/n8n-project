import { FastifyInstance } from 'fastify';
import { prisma } from '../utils/prisma';

export async function dashboardRoutes(app: FastifyInstance) {
  app.get('/api/dashboard/stats', {
    preHandler: [app.authenticate],
  }, async () => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const [
      totalProductions,
      completedToday,
      failedToday,
      activeProductions,
      channels,
      recentProductions,
    ] = await Promise.all([
      prisma.production.count(),
      prisma.production.count({
        where: { status: 'completed', completedAt: { gte: today } },
      }),
      prisma.production.count({
        where: { status: 'failed', completedAt: { gte: today } },
      }),
      prisma.production.count({
        where: {
          status: {
            in: ['pending', 'triggered', 'ai_generating', 'tts_processing', 'image_generating', 'video_rendering', 'uploading'],
          },
        },
      }),
      prisma.channel.findMany({
        include: {
          _count: { select: { productions: true } },
          productions: {
            take: 1,
            orderBy: { createdAt: 'desc' },
            select: { createdAt: true },
          },
        },
      }),
      prisma.production.findMany({
        take: 10,
        orderBy: { createdAt: 'desc' },
        include: {
          workflow: true,
          channel: true,
        },
      }),
    ]);

    const channelStats = channels.map((ch) => ({
      channelId: ch.id,
      channelName: ch.name,
      channelSlug: ch.slug,
      totalProductions: ch._count.productions,
      lastProductionAt: ch.productions[0]?.createdAt || null,
    }));

    return {
      success: true,
      data: {
        totalProductions,
        completedToday,
        failedToday,
        activeProductions,
        channelStats,
        recentProductions,
      },
    };
  });

  // Health check (no auth)
  app.get('/api/health', async () => {
    return { status: 'ok', timestamp: new Date().toISOString() };
  });
}
