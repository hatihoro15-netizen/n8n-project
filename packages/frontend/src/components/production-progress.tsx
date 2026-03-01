'use client';

import { cn } from '@/lib/utils';
import { Check, Loader2, X, Circle } from 'lucide-react';
import type { ProductionStatus } from '@n8n-web/shared';

const STEPS: { key: ProductionStatus; label: string }[] = [
  { key: 'pending', label: '대기' },
  { key: 'started', label: '시작' },
  { key: 'script_ready', label: 'AI 스크립트' },
  { key: 'tts_ready', label: 'TTS 음성' },
  { key: 'images_ready', label: '이미지' },
  { key: 'rendering', label: '영상 렌더링' },
  { key: 'completed', label: '완료' },
];

const STATUS_ORDER: Record<string, number> = {};
STEPS.forEach((s, i) => {
  STATUS_ORDER[s.key] = i;
});

interface ProductionProgressProps {
  status: ProductionStatus;
  className?: string;
}

export function ProductionProgress({ status, className }: ProductionProgressProps) {
  const isFailed = status === 'failed';
  const currentIdx = STATUS_ORDER[status] ?? -1;

  return (
    <div className={cn('flex items-center gap-1', className)}>
      {STEPS.map((step, idx) => {
        const isAllDone = status === 'completed';
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
                  isCurrent && !isFailed && 'border-blue-500 bg-blue-50 text-blue-600',
                  isCurrent && isFailed && 'border-red-500 bg-red-50 text-red-600',
                  isUpcoming && 'border-muted-foreground/20 text-muted-foreground/40'
                )}
              >
                {isCompleted ? (
                  <Check className="h-4 w-4" />
                ) : isCurrent && isFailed ? (
                  <X className="h-4 w-4" />
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
                  isCurrent && !isFailed && 'text-blue-600',
                  isCurrent && isFailed && 'text-red-600',
                  isUpcoming && 'text-muted-foreground/50'
                )}
              >
                {step.label}
              </span>
            </div>

            {/* Connector line */}
            {idx < STEPS.length - 1 && (
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
