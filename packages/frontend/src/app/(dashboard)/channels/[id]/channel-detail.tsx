'use client';

import { useParams } from 'next/navigation';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { StatusBadge } from '@/components/status-badge';
import { useChannel } from '@/hooks/use-dashboard';
import { useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Workflow, ArrowLeft, Trash2, Youtube, Plus } from 'lucide-react';
import Link from 'next/link';

export default function ChannelDetail() {
  const params = useParams();
  const { data, isLoading } = useChannel(params.id as string);
  const channel = data?.data;
  const queryClient = useQueryClient();

  const handleDeleteWorkflow = async (e: React.MouseEvent, wfId: string, name: string, prodCount: number) => {
    e.preventDefault();
    e.stopPropagation();
    if (prodCount > 0) {
      alert(`제작 이력이 ${prodCount}건 있어 삭제할 수 없습니다.`);
      return;
    }
    if (!confirm(`"${name}" 워크플로우를 삭제하시겠습니까?`)) return;
    try {
      await api.delete(`/api/workflows/${wfId}`);
      queryClient.invalidateQueries({ queryKey: ['channels', params.id] });
    } catch (err: any) {
      alert(err.message || '삭제에 실패했습니다.');
    }
  };

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

        {/* 워크플로우 */}
        <div>
          <h2 className="text-lg font-semibold mb-4">워크플로우</h2>
          <div className="grid gap-4 md:grid-cols-2">
            {channel.workflows?.map((wf: any) => (
              <Link key={wf.id} href={`/workflows/${wf.id}`}>
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Workflow className="h-5 w-5 text-primary" />
                        <div>
                          <h3 className="font-medium">{wf.name}</h3>
                          <p className="text-xs text-muted-foreground">
                            {wf.type} | 제작 {wf._count?.productions || 0}건
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={(e) => handleDeleteWorkflow(e, wf.id, wf.name, wf._count?.productions || 0)}
                        className="p-1.5 rounded-md text-muted-foreground/50 hover:text-red-600 hover:bg-red-50 transition-colors"
                        title="워크플로우 삭제"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </div>

        {/* 유튜브 계정 */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">유튜브 계정</h2>
            <Button
              variant="outline"
              size="sm"
              onClick={() => alert('준비 중입니다 (Phase 5에서 구현 예정)')}
            >
              <Plus className="h-4 w-4 mr-2" />
              계정 추가
            </Button>
          </div>
          <Card>
            <CardContent className="p-8 text-center text-muted-foreground">
              <Youtube className="h-10 w-10 mx-auto mb-3 text-muted-foreground/30" />
              <p className="text-sm">연결된 유튜브 계정이 없습니다</p>
              <p className="text-xs mt-1">Phase 5에서 OAuth 연동이 추가됩니다</p>
            </CardContent>
          </Card>
        </div>

        {/* 최근 제작 */}
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
