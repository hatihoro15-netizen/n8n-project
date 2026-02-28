import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.resolve(__dirname, '../.env') });

export const config = {
  port: parseInt(process.env.PORT || '3001', 10),
  host: process.env.HOST || '0.0.0.0',

  jwtSecret: process.env.JWT_SECRET || 'dev-secret-change-in-production',

  n8n: {
    baseUrl: process.env.N8N_BASE_URL || 'https://n8n.srv1345711.hstgr.cloud',
    apiKey: process.env.N8N_API_KEY || '',
    webhookBase: process.env.N8N_WEBHOOK_BASE || 'https://n8n.srv1345711.hstgr.cloud/webhook',
  },

  admin: {
    username: process.env.ADMIN_USERNAME || 'admin',
    password: process.env.ADMIN_PASSWORD || 'changeme',
  },

  corsOrigin: process.env.CORS_ORIGIN || 'http://localhost:3000',
};
