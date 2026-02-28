import { FastifyInstance } from 'fastify';
import { prisma } from '../utils/prisma';
import { n8nClient } from '../utils/n8n-client';

export async function workflowRoutes(app: FastifyInstance) {
  // List all workflows
  app.get('/api/workflows', {
    preHandler: [app.authenticate],
  }, async () => {
    const workflows = await prisma.workflow.findMany({
      include: {
        channel: true,
        _count: { select: { productions: true, prompts: true } },
      },
      orderBy: { name: 'asc' },
    });

    return { success: true, data: workflows };
  });

  // Get single workflow
  app.get('/api/workflows/:id', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const { id } = request.params as { id: string };

    const workflow = await prisma.workflow.findUnique({
      where: { id },
      include: {
        channel: true,
        prompts: {
          orderBy: { version: 'desc' },
        },
        characters: {
          include: { character: true },
        },
        productions: {
          take: 10,
          orderBy: { createdAt: 'desc' },
        },
      },
    });

    if (!workflow) {
      return reply.status(404).send({
        success: false,
        message: '워크플로우를 찾을 수 없습니다.',
      });
    }

    return { success: true, data: workflow };
  });

  // Get n8n workflow details (proxy)
  app.get('/api/workflows/:id/n8n', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const { id } = request.params as { id: string };

    const workflow = await prisma.workflow.findUnique({ where: { id } });
    if (!workflow) {
      return reply.status(404).send({ success: false, message: '워크플로우를 찾을 수 없습니다.' });
    }

    try {
      const n8nWorkflow = await n8nClient.getWorkflow(workflow.n8nWorkflowId);
      return { success: true, data: n8nWorkflow };
    } catch (error) {
      return reply.status(502).send({
        success: false,
        message: `n8n 연결 실패: ${error instanceof Error ? error.message : 'Unknown error'}`,
      });
    }
  });

  // Get n8n executions for a workflow
  app.get('/api/workflows/:id/executions', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const { id } = request.params as { id: string };

    const workflow = await prisma.workflow.findUnique({ where: { id } });
    if (!workflow) {
      return reply.status(404).send({ success: false, message: '워크플로우를 찾을 수 없습니다.' });
    }

    try {
      const executions = await n8nClient.getExecutions(workflow.n8nWorkflowId);
      return { success: true, data: executions.data };
    } catch (error) {
      return reply.status(502).send({
        success: false,
        message: `n8n 연결 실패: ${error instanceof Error ? error.message : 'Unknown error'}`,
      });
    }
  });

  // Update workflow
  app.put('/api/workflows/:id', {
    preHandler: [app.authenticate],
  }, async (request) => {
    const { id } = request.params as { id: string };
    const body = request.body as {
      name?: string;
      webhookPath?: string;
      scheduleExpression?: string;
      isActive?: boolean;
    };

    const workflow = await prisma.workflow.update({
      where: { id },
      data: body,
      include: { channel: true },
    });

    return { success: true, data: workflow };
  });
}
