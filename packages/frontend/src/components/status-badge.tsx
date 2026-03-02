'use client';

import { Badge } from '@/components/ui/badge';
import type { ProductionStatus } from '@n8n-web/shared';

const statusConfig: Record<ProductionStatus, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning' }> = {
  pending: { label: '대기', variant: 'secondary' },
  started: { label: '시작됨', variant: 'default' },
  script_ready: { label: 'AI 스크립트 완료', variant: 'warning' },
  tts_ready: { label: 'TTS 음성 완료', variant: 'warning' },
  images_ready: { label: '이미지 완료', variant: 'warning' },
  videos_ready: { label: 'AI 영상 완료', variant: 'warning' },
  rendering: { label: '영상 렌더링 중', variant: 'warning' },
  uploading: { label: '업로드 중', variant: 'default' },
  completed: { label: '완료', variant: 'success' },
  failed: { label: '실패', variant: 'destructive' },
  paused: { label: '정지됨', variant: 'outline' },
};

export function StatusBadge({ status }: { status: ProductionStatus }) {
  const config = statusConfig[status] || { label: status, variant: 'outline' as const };
  return <Badge variant={config.variant}>{config.label}</Badge>;
}
