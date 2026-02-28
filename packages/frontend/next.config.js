/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['@n8n-web/shared'],
  images: {
    unoptimized: true,
  },
};

module.exports = nextConfig;
