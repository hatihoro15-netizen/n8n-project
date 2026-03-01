'use client';

import { Header } from '@/components/layout/header';
import { Card, CardContent } from '@/components/ui/card';
import { Image } from 'lucide-react';

export default function MediaClient() {
  return (
    <>
      <Header title="미디어" />
      <div className="p-6">
        <Card>
          <CardContent className="p-12 text-center text-muted-foreground">
            <Image className="h-16 w-16 mx-auto mb-4 text-muted-foreground/30" />
            <h3 className="text-lg font-medium mb-2">미디어 라이브러리</h3>
            <p className="text-sm">Phase 4에서 생성된 이미지/영상을 브라우징할 수 있습니다.</p>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
