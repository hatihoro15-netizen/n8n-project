'use client';

import { Header } from '@/components/layout/header';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { FileText } from 'lucide-react';

export default function PromptsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['prompts'],
    queryFn: () => api.get<{ success: boolean; data: any[] }>('/api/prompts'),
  });

  const prompts = data?.data || [];

  return (
    <>
      <Header title="프롬프트" />
      <div className="p-6">
        {isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="p-4">
                  <div className="h-16 bg-muted rounded" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : prompts.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center text-muted-foreground">
              <FileText className="h-12 w-12 mx-auto mb-4 text-muted-foreground/50" />
              <p>등록된 프롬프트가 없습니다.</p>
              <p className="text-sm mt-1">워크플로우 상세 페이지에서 프롬프트를 추가할 수 있습니다.</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {prompts.map((prompt: any) => (
              <Card key={prompt.id}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-primary" />
                      <span className="font-medium">{prompt.nodeName}</span>
                      <Badge variant="outline" className="text-xs">
                        v{prompt.version}
                      </Badge>
                      {prompt.isDeployed && <Badge variant="success">배포됨</Badge>}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {prompt.workflow?.channel?.name} / {prompt.workflow?.name}
                    </div>
                  </div>
                  <pre className="text-xs text-muted-foreground bg-muted p-3 rounded max-h-32 overflow-y-auto whitespace-pre-wrap">
                    {prompt.content?.substring(0, 300)}
                    {prompt.content?.length > 300 ? '...' : ''}
                  </pre>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
