import { FastifyInstance } from 'fastify';
import { config } from '../config';

export async function authRoutes(app: FastifyInstance) {
  app.post('/api/auth/login', async (request, reply) => {
    const { username, password } = request.body as {
      username: string;
      password: string;
    };

    if (username !== config.admin.username || password !== config.admin.password) {
      return reply.status(401).send({
        success: false,
        message: '아이디 또는 비밀번호가 올바르지 않습니다.',
      });
    }

    const token = app.jwt.sign(
      { sub: 'admin', username },
      { expiresIn: '7d' }
    );

    return {
      success: true,
      data: {
        token,
        user: { id: 'admin', username },
      },
    };
  });

  app.get('/api/auth/me', {
    preHandler: [app.authenticate],
  }, async (request) => {
    return {
      success: true,
      data: { id: 'admin', username: config.admin.username },
    };
  });
}
