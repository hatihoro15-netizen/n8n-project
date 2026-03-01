import Fastify from 'fastify';
import cors from '@fastify/cors';
import jwt from '@fastify/jwt';
import { config } from './config';
import { logger } from './utils/logger';
import { prisma } from './utils/prisma';

// Routes
import { authRoutes } from './routes/auth';
import { dashboardRoutes } from './routes/dashboard';
import { channelRoutes } from './routes/channels';
import { workflowRoutes } from './routes/workflows';
import { productionRoutes } from './routes/productions';
import { promptRoutes } from './routes/prompts';
import { characterRoutes } from './routes/characters';

// Extend Fastify types
declare module 'fastify' {
  interface FastifyInstance {
    authenticate: (request: import('fastify').FastifyRequest, reply: import('fastify').FastifyReply) => Promise<void>;
  }
}

declare module '@fastify/jwt' {
  interface FastifyJWT {
    payload: { sub: string; username: string };
    user: { sub: string; username: string };
  }
}

async function buildServer() {
  const app = Fastify({
    logger: {
      transport:
        process.env.NODE_ENV !== 'production'
          ? { target: 'pino-pretty', options: { colorize: true } }
          : undefined,
    },
  });

  // CORS
  await app.register(cors, {
    origin: config.corsOrigin.split(','),
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  });

  // JWT
  await app.register(jwt, {
    secret: config.jwtSecret,
  });

  // Auth decorator
  app.decorate('authenticate', async function (
    request: import('fastify').FastifyRequest,
    reply: import('fastify').FastifyReply
  ) {
    try {
      await request.jwtVerify();
    } catch (err) {
      reply.status(401).send({ success: false, message: '인증이 필요합니다.' });
    }
  });

  // Register routes
  await app.register(authRoutes);
  await app.register(dashboardRoutes);
  await app.register(channelRoutes);
  await app.register(workflowRoutes);
  await app.register(productionRoutes);
  await app.register(promptRoutes);
  await app.register(characterRoutes);

  return app;
}

async function start() {
  const app = await buildServer();

  try {
    // Connect to database
    await prisma.$connect();
    logger.info('Database connected');

    await app.listen({ port: config.port, host: config.host });
    logger.info(`Server running at http://${config.host}:${config.port}`);
  } catch (err) {
    logger.error(err, 'Server failed to start');
    process.exit(1);
  }
}

start();
