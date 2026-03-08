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

// ── 능동 상태 동기화: 진행중 + executionId 있는 건을 n8n API로 확인 ──
async function syncActiveProductions() {
  try {
    const activeProductions = await prisma.production.findMany({
      where: {
        status: { in: [...IN_PROGRESS_STATUSES] },
        n8nExecutionId: { not: null },
      },
      select: { id: true, status: true, updatedAt: true, n8nExecutionId: true },
    });

    if (activeProductions.length === 0) return;

    let syncedCount = 0;
    let failedCount = 0;

    for (const prod of activeProductions) {
      try {
        const execution = await n8nClient.getExecution(prod.n8nExecutionId!);

        if (!execution.finished && (execution.status === 'running' || execution.status === 'waiting')) {
          // 정상 실행 중 → updatedAt 갱신 (타임아웃 시계 리셋)
          await prisma.production.update({
            where: { id: prod.id },
            data: { updatedAt: new Date() },
          });
          syncedCount++;
        } else if (execution.finished && execution.status === 'success') {
          // n8n 완료인데 콜백 안 온 건
          await prisma.production.update({
            where: { id: prod.id },
            data: {
              status: 'failed',
              errorMessage: '콜백 미수신: n8n 실행은 완료되었으나 콜백이 도착하지 않음',
              completedAt: new Date(),
            },
          });
          failedCount++;

          logger.warn(
            { productionId: prod.id, executionId: prod.n8nExecutionId },
            'Sync: n8n execution succeeded but callback not received'
          );
        } else {
          // error, stopped, crashed 등
          await prisma.production.update({
            where: { id: prod.id },
            data: {
              status: 'failed',
              errorMessage: `n8n 실행 실패 (status: ${execution.status})`,
              completedAt: new Date(),
            },
          });
          failedCount++;

          logger.info(
            { productionId: prod.id, executionId: prod.n8nExecutionId, n8nStatus: execution.status },
            'Sync: n8n execution not running'
          );
        }
      } catch (err) {
        // API 호출 실패 → skip (타임아웃 안전망에 위임)
        logger.warn(
          { productionId: prod.id, executionId: prod.n8nExecutionId, error: err },
          'Sync: failed to check n8n execution — skipping'
        );
      }
    }

    logger.info(
      `Active sync: ${activeProductions.length}건 확인, ${syncedCount}건 정상, ${failedCount}건 실패 처리`
    );
  } catch (err) {
    logger.error(err, 'Active sync error');
  }
}

// ── 타임아웃 안전망: 20분 초과 + executionId 없는 건 즉시 실패 처리 ──
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

    if (staleProductions.length === 0) return;

    let failedCount = 0;

    for (const prod of staleProductions) {
      try {
        const elapsedMin = Math.round((Date.now() - prod.updatedAt.getTime()) / 60000);

        if (prod.n8nExecutionId) {
          // executionId 있는데 여기까지 온 건 = sync에서 API 실패했던 건
          // 한 번 더 시도
          try {
            const execution = await n8nClient.getExecution(prod.n8nExecutionId);

            if (!execution.finished && (execution.status === 'running' || execution.status === 'waiting')) {
              await prisma.production.update({
                where: { id: prod.id },
                data: { updatedAt: new Date() },
              });

              logger.info(
                { productionId: prod.id, executionId: prod.n8nExecutionId },
                'Timeout: still running in n8n — timeout extended'
              );
              continue;
            }

            // 실패/완료 상태
            const msg = execution.finished && execution.status === 'success'
              ? `콜백 미수신: n8n 실행은 완료되었으나 콜백이 도착하지 않음 (${elapsedMin}분 경과)`
              : `n8n 실행 실패 (status: ${execution.status}, ${elapsedMin}분 경과)`;

            await prisma.production.update({
              where: { id: prod.id },
              data: { status: 'failed', errorMessage: msg, completedAt: new Date() },
            });
            failedCount++;

            logger.info(
              { productionId: prod.id, executionId: prod.n8nExecutionId, n8nStatus: execution.status },
              'Timeout: n8n execution not running'
            );
          } catch {
            // API 여전히 실패 → 안전하게 타임아웃 처리
            await prisma.production.update({
              where: { id: prod.id },
              data: {
                status: 'failed',
                errorMessage: `타임아웃: ${elapsedMin}분간 응답 없음 (n8n 상태 확인 실패)`,
                completedAt: new Date(),
              },
            });
            failedCount++;

            logger.warn(
              { productionId: prod.id, executionId: prod.n8nExecutionId, elapsedMinutes: elapsedMin },
              'Timeout: n8n API failed — forced timeout'
            );
          }
        } else {
          // executionId 없음 → 즉시 타임아웃
          await prisma.production.update({
            where: { id: prod.id },
            data: {
              status: 'failed',
              errorMessage: `타임아웃: 마지막 상태 업데이트 후 ${elapsedMin}분간 응답 없음`,
              completedAt: new Date(),
            },
          });
          failedCount++;

          logger.info(
            { productionId: prod.id, lastStatus: prod.status, elapsedMinutes: elapsedMin },
            'Timeout: no executionId'
          );
        }
      } catch (err) {
        logger.error(
          { productionId: prod.id, error: err },
          'Error handling timed out production'
        );
      }
    }

    logger.info(
      `Timeout checker: ${staleProductions.length}건 확인, ${failedCount}건 타임아웃 처리`
    );
  } catch (err) {
    logger.error(err, 'Timeout checker error');
  }
}

// ── 1분마다 sync → timeout 순서로 실행 ──
async function runChecks() {
  await syncActiveProductions();
  await checkTimeouts();
}

export function startTimeoutChecker() {
  if (intervalId) return;
  intervalId = setInterval(runChecks, 60_000);
  logger.info(
    `Timeout checker started (interval: 1min, timeout: ${config.productionTimeoutMinutes}min, active sync: enabled)`
  );
  runChecks();
}

export function stopTimeoutChecker() {
  if (intervalId) {
    clearInterval(intervalId);
    intervalId = null;
  }
}
