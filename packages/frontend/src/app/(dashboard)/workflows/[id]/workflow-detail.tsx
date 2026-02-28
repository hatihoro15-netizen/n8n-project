'use client';

import { useParams } from 'next/navigation';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { StatusBadge } from '@/components/status-badge';
import { Button } from '@/components/ui/button';
import { useWorkflow } from '@/hooks/use-dashboard';
import { ArrowLeft, Play, FileText, Users } from 'lucide-react';
import Link from 'next/link';

export default function WorkflowDetail() {
  const params = useParams();
  const { data, isLoading } = useWorkflow(params.id as string);
  const workflow = data?.data as any;

  if (isLoading) {
    return (
      <>
        <Header title="워크플로우 상세" />
        <div className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-32 bg-muted rounded-lg" />
            <div className="h-64 bg-muted rounded-lg" />
          </div>
        </div>
      </>
    );
  }

  if (!workflow) return null;

  const typeLabel: Record<string, string> = {
    shortform: '숏폼',
    longform: '롱폼',
    story_shorts: '스토리짤',
  };

  return (
    <>
      <Header title={workflow.name} />
      <div className="p-6 space-y-6">
        <Link href="/workflows">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            워크플로우 목록
          </Button>
        </Link>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>{workflow.name}</CardTitle>
              <div className="flex items-center gap-2">
                <Badge variant="secondary">{typeLabel[workflow.type] || workflow.type}</Badge>
                <Badge variant={workflow.isActive ? 'success' : 'secondary'}>
                  {workflow.isActive ? '활성' : '비활성'}
                </Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">채널:</span>{' '}
                <Link href={`/channels/${workflow.channel?.id}`} className="text-primary hover:underline">
                  {workflow.channel?.name}
                </Link>
              </div>
              <div>
                <span className="text-muted-foreground">n8n ID:</span>{' '}
                <code className="text-xs bg-muted px-1.5 py-0.5 rounded">{workflow.n8nWorkflowId}</code>
              </div>
              <div>
                <span className="text-muted-foreground">웹훅:</span>{' '}
                <code className="text-xs bg-muted px-1.5 py-0.5 rounded">{workflow.webhookUrl || '-'}</code>
              </div>
              <div>
                <span className="text-muted-foreground">스케줄:</span>{' '}
                {workflow.scheduleExpression || '수동'}
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                <CardTitle className="text-base">프롬프트</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              {workflow.prompts?.length === 0 ? (
                <p className="text-sm text-muted-foreground">등록된 프롬프트가 없습니다.</p>
              ) : (
                <div className="space-y-2">
                  {workflow.prompts?.map((p: any) => (
                    <div key={p.id} className="flex items-center justify-between p-2 rounded border">
                      <div>
                        <span className="font-medium text-sm">{p.nodeName}</span>
                        <span className="text-xs text-muted-foreground ml-2">v{p.version}</span>
                      </div>
                      {p.isDeployed && <Badge variant="success">배포됨</Badge>}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                <CardTitle className="text-base">캐릭터</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              {workflow.characters?.length === 0 ? (
                <p className="text-sm text-muted-foreground">연결된 캐릭터가 없습니다.</p>
              ) : (
                <div className="space-y-2">
                  {workflow.characters?.map((wc: any) => (
                    <div key={wc.characterId} className="flex items-center justify-between p-2 rounded border">
                      <div>
                        <span className="font-medium text-sm">{wc.character?.nameKo}</span>
                        <span className="text-xs text-muted-foreground ml-2">({wc.character?.name})</span>
                      </div>
                      <Badge variant="outline">{wc.role}</Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Play className="h-5 w-5" />
              <CardTitle className="text-base">최근 제작</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="px-4 py-3 text-left font-medium">제목</th>
                  <th className="px-4 py-3 text-left font-medium">상태</th>
                  <th className="px-4 py-3 text-left font-medium">일시</th>
                </tr>
              </thead>
              <tbody>
                {workflow.productions?.length === 0 ? (
                  <tr>
                    <td colSpan={3} className="px-4 py-8 text-center text-muted-foreground">
                      아직 제작 이력이 없습니다.
                    </td>
                  </tr>
                ) : (
                  workflow.productions?.map((prod: any) => (
                    <tr key={prod.id} className="border-b hover:bg-muted/50">
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
    </>
  );
}
