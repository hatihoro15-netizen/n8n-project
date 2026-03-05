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

  minio: {
    endpoint: process.env.MINIO_ENDPOINT || 'http://76.13.182.180:9000',
    accessKey: process.env.MINIO_ACCESS_KEY || '',
    secretKey: process.env.MINIO_SECRET_KEY || '',
    bucket: process.env.MINIO_BUCKET || 'arubto',
    region: process.env.MINIO_REGION || 'us-east-1',
  },

  corsOrigin: process.env.CORS_ORIGIN || 'http://localhost:3000',

  productionTimeoutMinutes: parseInt(process.env.PRODUCTION_TIMEOUT_MINUTES || '5', 10),
};
