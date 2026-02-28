import { FastifyInstance } from 'fastify';
import { Prisma } from '@prisma/client';
import { prisma } from '../utils/prisma';

export async function characterRoutes(app: FastifyInstance) {
  // List characters
  app.get('/api/characters', {
    preHandler: [app.authenticate],
  }, async () => {
    const characters = await prisma.character.findMany({
      include: {
        workflows: {
          include: { workflow: { include: { channel: true } } },
        },
      },
      orderBy: { name: 'asc' },
    });

    return { success: true, data: characters };
  });

  // Get single character
  app.get('/api/characters/:id', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const { id } = request.params as { id: string };

    const character = await prisma.character.findUnique({
      where: { id },
      include: {
        workflows: {
          include: { workflow: { include: { channel: true } } },
        },
      },
    });

    if (!character) {
      return reply.status(404).send({ success: false, message: '캐릭터를 찾을 수 없습니다.' });
    }

    return { success: true, data: character };
  });

  // Create character
  app.post('/api/characters', {
    preHandler: [app.authenticate],
  }, async (request) => {
    const body = request.body as {
      name: string;
      nameKo: string;
      personality?: string;
      speechStyle?: string;
      voiceId?: string;
      voiceSettings?: Prisma.InputJsonValue;
      imageUrl?: string;
    };

    const character = await prisma.character.create({ data: body });
    return { success: true, data: character };
  });

  // Update character
  app.put('/api/characters/:id', {
    preHandler: [app.authenticate],
  }, async (request) => {
    const { id } = request.params as { id: string };
    const body = request.body as {
      name?: string;
      nameKo?: string;
      personality?: string;
      speechStyle?: string;
      voiceId?: string;
      voiceSettings?: Prisma.InputJsonValue;
      imageUrl?: string;
      isActive?: boolean;
    };

    const character = await prisma.character.update({
      where: { id },
      data: body,
    });

    return { success: true, data: character };
  });

  // Delete character
  app.delete('/api/characters/:id', {
    preHandler: [app.authenticate],
  }, async (request) => {
    const { id } = request.params as { id: string };

    await prisma.character.update({
      where: { id },
      data: { isActive: false },
    });

    return { success: true, message: '캐릭터가 비활성화되었습니다.' };
  });
}
