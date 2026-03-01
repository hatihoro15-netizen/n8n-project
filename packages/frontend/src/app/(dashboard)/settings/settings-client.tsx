'use client';

import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Settings, CheckCircle, XCircle, RefreshCw } from 'lucide-react';

export default function SettingsClient() {
  const { data: health, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['health'],
    queryFn: () => api.get<{ status: string; timestamp: string }>('/api/health'),
    retry: false,
  });

  return (
    <>
      <Header title="설정" />
      <div className="p-6 space-y-6">
        {/* System Status */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                시스템 상태
              </CardTitle>
              <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isRefetching}>
                <RefreshCw className={`h-4 w-4 mr-2 ${isRefetching ? 'animate-spin' : ''}`} />
                새로고침
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 rounded-lg border">
                <div className="flex items-center gap-3">
                  {health?.status === 'ok' ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600" />
                  )}
                  <div>
                    <p className="font-medium">백엔드 API</p>
                    <p className="text-xs text-muted-foreground">Fastify 서버</p>
                  </div>
                </div>
                <Badge variant={health?.status === 'ok' ? 'success' : 'destructive'}>
                  {isLoading ? '확인 중...' : health?.status === 'ok' ? '정상' : '오류'}
                </Badge>
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg border">
                <div className="flex items-center gap-3">
                  <div className="h-5 w-5 rounded-full bg-blue-500" />
                  <div>
                    <p className="font-medium">n8n 서버</p>
                    <p className="text-xs text-muted-foreground">워크플로우 엔진</p>
                  </div>
                </div>
                <Badge variant="outline">연결 확인 필요</Badge>
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg border">
                <div className="flex items-center gap-3">
                  <div className="h-5 w-5 rounded-full bg-green-500" />
                  <div>
                    <p className="font-medium">PostgreSQL</p>
                    <p className="text-xs text-muted-foreground">데이터베이스</p>
                  </div>
                </div>
                <Badge variant={health?.status === 'ok' ? 'success' : 'destructive'}>
                  {health?.status === 'ok' ? '정상' : '확인 필요'}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* API Info */}
        <Card>
          <CardHeader>
            <CardTitle>API 정보</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">API URL</span>
                <code className="text-xs bg-muted px-2 py-1 rounded">
                  {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001'}
                </code>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">버전</span>
                <span>v0.1.0</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
