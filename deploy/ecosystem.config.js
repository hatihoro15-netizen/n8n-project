module.exports = {
  apps: [
    {
      name: 'n8n-web-backend',
      script: 'dist/server.js',
      cwd: '/root/n8n-web/packages/backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production',
        PORT: 3001,
        HOST: '0.0.0.0',
      },
    },
  ],
};
