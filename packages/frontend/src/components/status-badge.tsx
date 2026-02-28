'use client';

import { Badge } from '@/components/ui/badge';
import type { ProductionStatus } from '@n8n-web/shared';

const statusConfig: Record<ProductionStatus, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning' }> = {
  pending: { label: '대기', variant: 'secondary' },
  triggered: { label: '시작됨', variant: 'default' },
  ai_generating: { label: 'AI 생성 중', variant: 'warning' },
  tts_processing: { label: 'TTS 처리 중', variant: 'warning' },
  image_generating: { label: '이미지 생성 중', variant: 'warning' },
  video_rendering: { label: '영상 렌더링 중', variant: 'warning' },
  uploading: { label: '업로드 중', variant: 'default' },
  completed: { label: '완료', variant: 'success' },
  failed: { label: '실패', variant: 'destructive' },
};

export function StatusBadge({ status }: { status: ProductionStatus }) {
  const config = statusConfig[status] || { label: status, variant: 'outline' as const };
  return <Badge variant={config.variant}>{config.label}</Badge>;
}
