'use client';

import { Header } from '@/components/layout/header';
import { Card, CardContent } from '@/components/ui/card';
import { BarChart3 } from 'lucide-react';

export default function AnalyticsPage() {
  return (
    <>
      <Header title="분석" />
      <div className="p-6">
        <Card>
          <CardContent className="p-12 text-center text-muted-foreground">
            <BarChart3 className="h-16 w-16 mx-auto mb-4 text-muted-foreground/30" />
            <h3 className="text-lg font-medium mb-2">분석 대시보드</h3>
            <p className="text-sm">Phase 4에서 YouTube Analytics API 연동 후 제공됩니다.</p>
            <p className="text-sm mt-1">조회수, CTR, 좋아요 등 채널별 성과 데이터를 확인할 수 있습니다.</p>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
