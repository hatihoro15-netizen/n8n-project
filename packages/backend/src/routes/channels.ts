import { FastifyInstance } from 'fastify';
import { prisma } from '../utils/prisma';

export async function channelRoutes(app: FastifyInstance) {
  // List all channels
  app.get('/api/channels', {
    preHandler: [app.authenticate],
  }, async () => {
    const channels = await prisma.channel.findMany({
      include: {
        workflows: true,
        _count: { select: { productions: true } },
      },
      orderBy: { name: 'asc' },
    });

    return {
      success: true,
      data: channels,
    };
  });

  // Get single channel with details
  app.get('/api/channels/:id', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const { id } = request.params as { id: string };

    const channel = await prisma.channel.findUnique({
      where: { id },
      include: {
        workflows: {
          include: {
            _count: { select: { productions: true } },
          },
        },
        productions: {
          take: 10,
          orderBy: { createdAt: 'desc' },
        },
      },
    });

    if (!channel) {
      return reply.status(404).send({
        success: false,
        message: '채널을 찾을 수 없습니다.',
      });
    }

    return { success: true, data: channel };
  });

  // Update channel
  app.put('/api/channels/:id', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const { id } = request.params as { id: string };
    const body = request.body as {
      name?: string;
      description?: string;
      youtubeChannelId?: string;
      thumbnailUrl?: string;
      isActive?: boolean;
    };

    const channel = await prisma.channel.update({
      where: { id },
      data: body,
    });

    return { success: true, data: channel };
  });
}
