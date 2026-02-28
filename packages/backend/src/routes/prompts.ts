import { FastifyInstance } from 'fastify';
import { prisma } from '../utils/prisma';
import { n8nClient } from '../utils/n8n-client';
import { logger } from '../utils/logger';

export async function promptRoutes(app: FastifyInstance) {
  // List prompts
  app.get('/api/prompts', {
    preHandler: [app.authenticate],
  }, async (request) => {
    const { workflowId } = request.query as { workflowId?: string };

    const where: Record<string, unknown> = {};
    if (workflowId) where.workflowId = workflowId;

    const prompts = await prisma.prompt.findMany({
      where,
      include: { workflow: { include: { channel: true } } },
      orderBy: [{ workflowId: 'asc' }, { nodeName: 'asc' }, { version: 'desc' }],
    });

    return { success: true, data: prompts };
  });

  // Get single prompt
  app.get('/api/prompts/:id', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const { id } = request.params as { id: string };

    const prompt = await prisma.prompt.findUnique({
      where: { id },
      include: { workflow: { include: { channel: true } } },
    });

    if (!prompt) {
      return reply.status(404).send({ success: false, message: '프롬프트를 찾을 수 없습니다.' });
    }

    return { success: true, data: prompt };
  });

  // Get version history for a prompt
  app.get('/api/prompts/history/:workflowId/:nodeName', {
    preHandler: [app.authenticate],
  }, async (request) => {
    const { workflowId, nodeName } = request.params as {
      workflowId: string;
      nodeName: string;
    };

    const prompts = await prisma.prompt.findMany({
      where: { workflowId, nodeName },
      orderBy: { version: 'desc' },
    });

    return { success: true, data: prompts };
  });

  // Create new prompt version
  app.post('/api/prompts', {
    preHandler: [app.authenticate],
  }, async (request) => {
    const { workflowId, nodeName, content } = request.body as {
      workflowId: string;
      nodeName: string;
      content: string;
    };

    // Get latest version
    const latest = await prisma.prompt.findFirst({
      where: { workflowId, nodeName },
      orderBy: { version: 'desc' },
    });

    const prompt = await prisma.prompt.create({
      data: {
        workflowId,
        nodeName,
        content,
        version: latest ? latest.version + 1 : 1,
      },
      include: { workflow: { include: { channel: true } } },
    });

    return { success: true, data: prompt };
  });

  // Deploy prompt to n8n
  app.post('/api/prompts/:id/deploy', {
    preHandler: [app.authenticate],
  }, async (request, reply) => {
    const { id } = request.params as { id: string };

    const prompt = await prisma.prompt.findUnique({
      where: { id },
      include: { workflow: true },
    });

    if (!prompt) {
      return reply.status(404).send({ success: false, message: '프롬프트를 찾을 수 없습니다.' });
    }

    try {
      // Fetch current workflow from n8n
      const n8nWorkflow = await n8nClient.getWorkflow(prompt.workflow.n8nWorkflowId);

      // Find the target node and update its prompt
      let updated = false;
      for (const node of n8nWorkflow.nodes) {
        if (node.name === prompt.nodeName) {
          const messages = (node.parameters as Record<string, unknown>).messages as
            | { values: { content: string }[] }
            | undefined;
          if (messages?.values?.[0]) {
            messages.values[0].content = prompt.content;
            updated = true;
          }
          break;
        }
      }

      if (!updated) {
        return reply.status(400).send({
          success: false,
          message: `n8n 워크플로우에서 '${prompt.nodeName}' 노드를 찾을 수 없습니다.`,
        });
      }

      // Upload back to n8n
      await n8nClient.updateWorkflow(prompt.workflow.n8nWorkflowId, {
        name: n8nWorkflow.name,
        nodes: n8nWorkflow.nodes,
        connections: n8nWorkflow.connections as Record<string, unknown>,
      });

      // Mark as deployed
      await prisma.prompt.updateMany({
        where: {
          workflowId: prompt.workflowId,
          nodeName: prompt.nodeName,
        },
        data: { isDeployed: false },
      });

      const deployedPrompt = await prisma.prompt.update({
        where: { id },
        data: { isDeployed: true, deployedAt: new Date() },
      });

      logger.info(
        { promptId: id, workflowId: prompt.workflowId, nodeName: prompt.nodeName },
        'Prompt deployed to n8n'
      );

      return { success: true, data: deployedPrompt };
    } catch (error) {
      logger.error({ promptId: id, error }, 'Failed to deploy prompt');
      return reply.status(502).send({
        success: false,
        message: `n8n 배포 실패: ${error instanceof Error ? error.message : 'Unknown error'}`,
      });
    }
  });
}
