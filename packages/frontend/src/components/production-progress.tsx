'use client';

import { cn } from '@/lib/utils';
import { Check, Loader2, X, Circle, Pause } from 'lucide-react';
import type { ProductionStatus, StepperType } from '@n8n-web/shared';

interface Step {
  key: ProductionStatus;
  label: string;
}

// TTS 기반 (설명형 숏폼): 대기 → 시작 → AI 스크립트 → TTS 음성 → 이미지 → 영상 렌더링 → 완료
const TTS_STEPS: Step[] = [
  { key: 'pending', label: '대기' },
  { key: 'started', label: '시작' },
  { key: 'script_ready', label: 'AI 스크립트' },
  { key: 'tts_ready', label: 'TTS 음성' },
  { key: 'images_ready', label: '이미지' },
  { key: 'rendering', label: '영상 렌더링' },
  { key: 'completed', label: '완료' },
];

// 영상 기반 (스토리형): 대기 → 시작 → AI 스크립트 → 이미지 → AI 영상 → 영상 렌더링 → 완료
const VIDEO_STEPS: Step[] = [
  { key: 'pending', label: '대기' },
  { key: 'started', label: '시작' },
  { key: 'script_ready', label: 'AI 스크립트' },
  { key: 'images_ready', label: '이미지' },
  { key: 'videos_ready', label: 'AI 영상' },
  { key: 'rendering', label: '영상 렌더링' },
  { key: 'completed', label: '완료' },
];

function buildOrderMap(steps: Step[]): Record<string, number> {
  const map: Record<string, number> = {};
  steps.forEach((s, i) => {
    map[s.key] = i;
  });
  return map;
}

interface ProductionProgressProps {
  status: ProductionStatus;
  stepperType?: StepperType;
  className?: string;
}

export function ProductionProgress({ status, stepperType = 'tts_based', className }: ProductionProgressProps) {
  const steps = stepperType === 'video_based' ? VIDEO_STEPS : TTS_STEPS;
  const orderMap = buildOrderMap(steps);

  const isFailed = status === 'failed';
  const isPaused = status === 'paused';
  const isAllDone = status === 'completed';

  // For failed/paused, find last known progress step
  // Use the step order to determine where the marker should be
  const currentIdx = orderMap[status] ?? -1;

  return (
    <div className={cn('flex items-center gap-1', className)}>
      {steps.map((step, idx) => {
        const isCompleted = isAllDone || currentIdx > idx;
        const isCurrent = !isAllDone && currentIdx === idx;
        const isUpcoming = !isAllDone && currentIdx < idx;

        return (
          <div key={step.key} className="flex items-center gap-1">
            {/* Step indicator */}
            <div className="flex flex-col items-center gap-1">
              <div
                className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-full border-2 transition-all',
                  isCompleted && 'border-emerald-500 bg-emerald-500 text-white',
                  isCurrent && !isFailed && !isPaused && 'border-blue-500 bg-blue-50 text-blue-600',
                  isCurrent && isFailed && 'border-red-500 bg-red-50 text-red-600',
                  isCurrent && isPaused && 'border-amber-500 bg-amber-50 text-amber-600',
                  isUpcoming && 'border-muted-foreground/20 text-muted-foreground/40'
                )}
              >
                {isCompleted ? (
                  <Check className="h-4 w-4" />
                ) : isCurrent && isFailed ? (
                  <X className="h-4 w-4" />
                ) : isCurrent && isPaused ? (
                  <Pause className="h-4 w-4" />
                ) : isCurrent ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Circle className="h-3 w-3" />
                )}
              </div>
              <span
                className={cn(
                  'text-[10px] font-medium whitespace-nowrap',
                  isCompleted && 'text-emerald-600',
                  isCurrent && !isFailed && !isPaused && 'text-blue-600',
                  isCurrent && isFailed && 'text-red-600',
                  isCurrent && isPaused && 'text-amber-600',
                  isUpcoming && 'text-muted-foreground/50'
                )}
              >
                {step.label}
              </span>
            </div>

            {/* Connector line */}
            {idx < steps.length - 1 && (
              <div
                className={cn(
                  'h-0.5 w-6 mb-5 rounded-full',
                  isCompleted ? 'bg-emerald-500' : 'bg-muted-foreground/15'
                )}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
