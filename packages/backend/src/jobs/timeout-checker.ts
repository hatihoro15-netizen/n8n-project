import { prisma } from '../utils/prisma';
import { logger } from '../utils/logger';
import { config } from '../config';

const IN_PROGRESS_STATUSES = [
  'started',
  'script_ready',
  'tts_ready',
  'images_ready',
  'videos_ready',
  'rendering',
  'uploading',
] as const;

let intervalId: ReturnType<typeof setInterval> | null = null;

async function checkTimeouts() {
  const timeoutMs = config.productionTimeoutMinutes * 60 * 1000;
  const cutoff = new Date(Date.now() - timeoutMs);

  try {
    const staleProductions = await prisma.production.findMany({
      where: {
        status: { in: [...IN_PROGRESS_STATUSES] },
        updatedAt: { lt: cutoff },
      },
      select: { id: true, status: true, updatedAt: true },
    });

    for (const prod of staleProductions) {
      const elapsedMin = Math.round((Date.now() - prod.updatedAt.getTime()) / 60000);

      await prisma.production.update({
        where: { id: prod.id },
        data: {
          status: 'failed',
          errorMessage: `타임아웃: 마지막 상태 업데이트 후 ${elapsedMin}분간 응답 없음`,
          completedAt: new Date(),
        },
      });

      logger.info(
        { productionId: prod.id, lastStatus: prod.status, elapsedMinutes: elapsedMin },
        'Production timed out'
      );
    }

    if (staleProductions.length > 0) {
      logger.info(`Timeout checker: ${staleProductions.length}건 타임아웃 처리`);
    }
  } catch (err) {
    logger.error(err, 'Timeout checker error');
  }
}

export function startTimeoutChecker() {
  if (intervalId) return;
  intervalId = setInterval(checkTimeouts, 60_000); // 1분마다
  logger.info(
    `Timeout checker started (interval: 1min, timeout: ${config.productionTimeoutMinutes}min)`
  );
  // 시작 직후 1회 실행
  checkTimeouts();
}

export function stopTimeoutChecker() {
  if (intervalId) {
    clearInterval(intervalId);
    intervalId = null;
  }
}
