#!/bin/bash
# VPS 배포 스크립트 (백엔드)
# 사용법: ssh root@vps 'bash -s' < deploy/deploy.sh

set -e

APP_DIR="/root/n8n-web"
REPO_URL="https://github.com/hatihoro15-netizen/n8n-project.git"
BRANCH="feature/web-app"

echo "=== n8n-web Backend Deployment ==="

# 1. 코드 업데이트
if [ -d "$APP_DIR" ]; then
    cd $APP_DIR
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH
else
    git clone -b $BRANCH $REPO_URL $APP_DIR
    cd $APP_DIR
fi

# 2. 의존성 설치
npm install --production=false

# 3. Prisma 생성
cd packages/backend
npx prisma generate
npx prisma migrate deploy

# 4. 빌드
npm run build

# 5. PM2 재시작
cd $APP_DIR
pm2 startOrRestart deploy/ecosystem.config.js --env production

echo "=== Deployment Complete ==="
pm2 status
