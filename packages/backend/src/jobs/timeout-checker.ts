import { prisma } from '../utils/prisma';
import { logger } from '../utils/logger';
import { config } from '../config';
import { n8nClient } from '../utils/n8n-client';

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

async function handleTimedOutProduction(prod: {
  id: string;
  status: string;
  updatedAt: Date;
  n8nExecutionId: string | null;
}) {
  const elapsedMin = Math.round((Date.now() - prod.updatedAt.getTime()) / 60000);

  // n8nExecutionId가 없으면 기존대로 즉시 failed
  if (!prod.n8nExecutionId) {
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
      'Production timed out (no executionId)'
    );
    return;
  }

  // n8n API로 실제 실행 상태 확인
  try {
    const execution = await n8nClient.getExecution(prod.n8nExecutionId);

    // 아직 실행 중 → updatedAt만 갱신 (타임아웃 연장)
    if (!execution.finished && execution.status === 'running') {
      await prisma.production.update({
        where: { id: prod.id },
        data: { updatedAt: new Date() },
      });

      logger.info(
        { productionId: prod.id, executionId: prod.n8nExecutionId, lastStatus: prod.status },
        'Production still running in n8n — timeout extended'
      );
      return;
    }

    // n8n에서는 완료됐는데 콜백이 안 온 경우
    if (execution.finished && execution.status === 'success') {
      await prisma.production.update({
        where: { id: prod.id },
        data: {
          status: 'failed',
          errorMessage: `콜백 미수신: n8n 실행은 완료되었으나 콜백이 도착하지 않음 (${elapsedMin}분 경과)`,
          completedAt: new Date(),
        },
      });

      logger.warn(
        { productionId: prod.id, executionId: prod.n8nExecutionId },
        'Production failed — n8n execution succeeded but callback not received'
      );
      return;
    }

    // 그 외 (error, stopped, crashed 등)
    await prisma.production.update({
      where: { id: prod.id },
      data: {
        status: 'failed',
        errorMessage: `n8n 실행 실패 (status: ${execution.status}, ${elapsedMin}분 경과)`,
        completedAt: new Date(),
      },
    });

    logger.info(
      { productionId: prod.id, executionId: prod.n8nExecutionId, n8nStatus: execution.status },
      'Production timed out — n8n execution not running'
    );
  } catch (err) {
    // n8n API 호출 실패 → 안전하게 failed 처리 (기존 동작)
    logger.warn(
      { productionId: prod.id, executionId: prod.n8nExecutionId, error: err },
      'Failed to check n8n execution status — falling back to timeout'
    );

    await prisma.production.update({
      where: { id: prod.id },
      data: {
        status: 'failed',
        errorMessage: `타임아웃: 마지막 상태 업데이트 후 ${elapsedMin}분간 응답 없음 (n8n 상태 확인 실패)`,
        completedAt: new Date(),
      },
    });

    logger.info(
      { productionId: prod.id, lastStatus: prod.status, elapsedMinutes: elapsedMin },
      'Production timed out (n8n API fallback)'
    );
  }
}

async function checkTimeouts() {
  const timeoutMs = config.productionTimeoutMinutes * 60 * 1000;
  const cutoff = new Date(Date.now() - timeoutMs);

  try {
    const staleProductions = await prisma.production.findMany({
      where: {
        status: { in: [...IN_PROGRESS_STATUSES] },
        updatedAt: { lt: cutoff },
      },
      select: { id: true, status: true, updatedAt: true, n8nExecutionId: true },
    });

    let failedCount = 0;

    for (const prod of staleProductions) {
      try {
        const before = await prisma.production.findUnique({
          where: { id: prod.id },
          select: { status: true },
        });

        await handleTimedOutProduction(prod);

        const after = await prisma.production.findUnique({
          where: { id: prod.id },
          select: { status: true },
        });

        if (after?.status === 'failed' && before?.status !== 'failed') {
          failedCount++;
        }
      } catch (err) {
        logger.error(
          { productionId: prod.id, error: err },
          'Error handling timed out production'
        );
      }
    }

    if (staleProductions.length > 0) {
      logger.info(
        `Timeout checker: ${staleProductions.length}건 확인, ${failedCount}건 타임아웃 처리`
      );
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
