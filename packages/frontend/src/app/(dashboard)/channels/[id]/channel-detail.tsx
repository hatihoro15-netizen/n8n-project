'use client';

import { useParams } from 'next/navigation';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { StatusBadge } from '@/components/status-badge';
import { useChannel } from '@/hooks/use-dashboard';
import { Workflow, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function ChannelDetail() {
  const params = useParams();
  const { data, isLoading } = useChannel(params.id as string);
  const channel = data?.data;

  if (isLoading) {
    return (
      <>
        <Header title="채널 상세" />
        <div className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-32 bg-muted rounded-lg" />
            <div className="h-64 bg-muted rounded-lg" />
          </div>
        </div>
      </>
    );
  }

  if (!channel) return null;

  return (
    <>
      <Header title={channel.name} />
      <div className="p-6 space-y-6">
        <Link href="/channels">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            채널 목록
          </Button>
        </Link>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>{channel.name}</CardTitle>
              <Badge variant={channel.isActive ? 'success' : 'secondary'}>
                {channel.isActive ? '활성' : '비활성'}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">{channel.description}</p>
          </CardContent>
        </Card>

        <div>
          <h2 className="text-lg font-semibold mb-4">워크플로우</h2>
          <div className="grid gap-4 md:grid-cols-2">
            {channel.workflows?.map((wf: any) => (
              <Link key={wf.id} href={`/workflows/${wf.id}`}>
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <Workflow className="h-5 w-5 text-primary" />
                      <div>
                        <h3 className="font-medium">{wf.name}</h3>
                        <p className="text-xs text-muted-foreground">
                          {wf.type} | 제작 {wf._count?.productions || 0}건
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-lg font-semibold mb-4">최근 제작</h2>
          <Card>
            <CardContent className="p-0">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="px-4 py-3 text-left font-medium">워크플로우</th>
                    <th className="px-4 py-3 text-left font-medium">제목</th>
                    <th className="px-4 py-3 text-left font-medium">상태</th>
                    <th className="px-4 py-3 text-left font-medium">일시</th>
                  </tr>
                </thead>
                <tbody>
                  {channel.productions?.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="px-4 py-8 text-center text-muted-foreground">
                        아직 제작 이력이 없습니다.
                      </td>
                    </tr>
                  ) : (
                    channel.productions?.map((prod: any) => (
                      <tr key={prod.id} className="border-b hover:bg-muted/50">
                        <td className="px-4 py-3">{prod.workflow?.name || '-'}</td>
                        <td className="px-4 py-3">{prod.title || prod.topic || '-'}</td>
                        <td className="px-4 py-3">
                          <StatusBadge status={prod.status} />
                        </td>
                        <td className="px-4 py-3 text-muted-foreground">
                          {new Date(prod.createdAt).toLocaleString('ko-KR')}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
}
