'use client';

import { Header } from '@/components/layout/header';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useWorkflows } from '@/hooks/use-dashboard';
import { Workflow, ExternalLink } from 'lucide-react';
import Link from 'next/link';

export default function WorkflowsPage() {
  const { data, isLoading } = useWorkflows();
  const workflows = data?.data;

  const typeLabel: Record<string, string> = {
    shortform: '숏폼',
    longform: '롱폼',
    story_shorts: '스토리짤',
  };

  return (
    <>
      <Header title="워크플로우" />
      <div className="p-6">
        <div className="grid gap-4">
          {isLoading
            ? Array.from({ length: 6 }).map((_, i) => (
                <Card key={i} className="animate-pulse">
                  <CardContent className="p-4">
                    <div className="h-16 bg-muted rounded" />
                  </CardContent>
                </Card>
              ))
            : workflows?.map((wf) => (
                <Link key={wf.id} href={`/workflows/${wf.id}`}>
                  <Card className="hover:shadow-md transition-shadow cursor-pointer">
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                            <Workflow className="h-5 w-5 text-primary" />
                          </div>
                          <div>
                            <h3 className="font-semibold">{wf.name}</h3>
                            <div className="flex items-center gap-2 mt-1">
                              <Badge variant="outline">{wf.channel?.name}</Badge>
                              <Badge variant="secondary">{typeLabel[wf.type] || wf.type}</Badge>
                              <span className="text-xs text-muted-foreground">
                                n8n: {wf.n8nWorkflowId}
                              </span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span>제작 {wf._count?.productions || 0}건</span>
                          <span>프롬프트 {wf._count?.prompts || 0}개</span>
                          <Badge variant={wf.isActive ? 'success' : 'secondary'}>
                            {wf.isActive ? '활성' : '비활성'}
                          </Badge>
                        </div>
                      </div>
                      {wf.webhookUrl && (
                        <p className="mt-2 text-xs text-muted-foreground flex items-center gap-1 ml-14">
                          <ExternalLink className="h-3 w-3" />
                          {wf.webhookUrl}
                        </p>
                      )}
                    </CardContent>
                  </Card>
                </Link>
              ))}
        </div>
      </div>
    </>
  );
}
