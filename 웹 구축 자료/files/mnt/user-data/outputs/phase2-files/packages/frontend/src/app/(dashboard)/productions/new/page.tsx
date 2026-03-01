'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useWorkflows } from '@/hooks/use-dashboard';
import { api } from '@/lib/api';
import { ArrowLeft, Play } from 'lucide-react';
import Link from 'next/link';

export default function NewProductionPage() {
  const router = useRouter();
  const { data } = useWorkflows();
  const workflows = data?.data;

  const [selectedWorkflow, setSelectedWorkflow] = useState('');
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedWorkflow) {
      setError('워크플로우를 선택해주세요.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await api.post<{ success: boolean; data: { id: string } }>('/api/productions', {
        workflowId: selectedWorkflow,
        topic: topic || undefined,
      });
      router.push(`/productions/${result.data.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : '제작 트리거에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const typeLabel: Record<string, string> = {
    shortform: '숏폼',
    longform: '롱폼',
    story_shorts: '스토리짤',
  };

  return (
    <>
      <Header title="새 제작" />
      <div className="p-6 space-y-6">
        <Link href="/productions">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            제작 목록
          </Button>
        </Link>

        <Card className="max-w-2xl">
          <CardHeader>
            <CardTitle>새 영상 제작</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Workflow Selection */}
              <div className="space-y-2">
                <label className="text-sm font-medium">워크플로우 선택</label>
                <div className="grid gap-2">
                  {workflows?.map((wf) => (
                    <label
                      key={wf.id}
                      className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                        selectedWorkflow === wf.id
                          ? 'border-primary bg-primary/5'
                          : 'hover:bg-muted/50'
                      }`}
                    >
                      <input
                        type="radio"
                        name="workflow"
                        value={wf.id}
                        checked={selectedWorkflow === wf.id}
                        onChange={(e) => setSelectedWorkflow(e.target.value)}
                        className="accent-primary"
                      />
                      <div>
                        <div className="font-medium text-sm">{wf.name}</div>
                        <div className="text-xs text-muted-foreground">
                          {wf.channel?.name} | {typeLabel[wf.type] || wf.type}
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Topic */}
              <div className="space-y-2">
                <label className="text-sm font-medium" htmlFor="topic">
                  주제 (선택사항)
                </label>
                <Input
                  id="topic"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="주제를 입력하면 해당 주제로 영상을 제작합니다"
                />
                <p className="text-xs text-muted-foreground">
                  비워두면 AI가 자동으로 주제를 생성합니다.
                </p>
              </div>

              {error && <p className="text-sm text-destructive">{error}</p>}

              <Button type="submit" disabled={loading || !selectedWorkflow}>
                <Play className="h-4 w-4 mr-2" />
                {loading ? '트리거 중...' : '제작 시작'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
