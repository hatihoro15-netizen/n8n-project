'use client';

import { useState } from 'react';
import { Header } from '@/components/layout/header';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useWorkflows, useChannels } from '@/hooks/use-dashboard';
import { useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Workflow, ExternalLink, Plus, Trash2, X } from 'lucide-react';
import Link from 'next/link';

export default function WorkflowsClient() {
  const { data, isLoading } = useWorkflows();
  const workflows = data?.data;
  const queryClient = useQueryClient();
  const [showAddForm, setShowAddForm] = useState(false);

  const typeLabel: Record<string, string> = {
    shortform: '숏폼',
    longform: '롱폼',
    story_shorts: '스토리짤',
  };

  const handleDelete = async (e: React.MouseEvent, wfId: string, name: string, prodCount: number) => {
    e.preventDefault();
    e.stopPropagation();
    if (prodCount > 0) {
      alert(`제작 이력이 ${prodCount}건 있어 삭제할 수 없습니다.`);
      return;
    }
    if (!confirm(`"${name}" 워크플로우를 삭제하시겠습니까?`)) return;
    try {
      await api.delete(`/api/workflows/${wfId}`);
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
    } catch (err: any) {
      alert(err.message || '삭제에 실패했습니다.');
    }
  };

  return (
    <>
      <Header title="워크플로우" />
      <div className="p-6 space-y-4">
        <div className="flex justify-end">
          <Button onClick={() => setShowAddForm(true)}>
            <Plus className="h-4 w-4 mr-2" />
            워크플로우 추가
          </Button>
        </div>

        {showAddForm && (
          <AddWorkflowForm
            onClose={() => setShowAddForm(false)}
            onCreated={() => {
              setShowAddForm(false);
              queryClient.invalidateQueries({ queryKey: ['workflows'] });
            }}
          />
        )}

        <div className="grid gap-4">
          {isLoading
            ? Array.from({ length: 6 }).map((_, i) => (
                <Card key={i} className="animate-pulse">
                  <CardContent className="p-4">
                    <div className="h-16 bg-muted rounded" />
                  </CardContent>
                </Card>
              ))
            : workflows?.map((wf: any) => (
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
                          <button
                            onClick={(e) => handleDelete(e, wf.id, wf.name, wf._count?.productions || 0)}
                            className="p-1.5 rounded-md text-muted-foreground/50 hover:text-red-600 hover:bg-red-50 transition-colors"
                            title="워크플로우 삭제"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
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

function AddWorkflowForm({
  onClose,
  onCreated,
}: {
  onClose: () => void;
  onCreated: () => void;
}) {
  const { data: channelsData } = useChannels();
  const channels = channelsData?.data;
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    name: '',
    channelId: '',
    type: 'shortform',
    n8nWorkflowId: '',
    webhookPath: '',
    stepperType: 'tts_based',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name || !form.channelId || !form.n8nWorkflowId) {
      alert('이름, 채널, n8n 워크플로우 ID는 필수입니다.');
      return;
    }
    setSubmitting(true);
    try {
      await api.post('/api/workflows', form);
      onCreated();
    } catch (err: any) {
      alert(err.message || '생성에 실패했습니다.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold">워크플로우 추가</h3>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground">
            <X className="h-4 w-4" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-muted-foreground">이름 *</label>
            <input
              className="w-full mt-1 px-3 py-2 border rounded-md text-sm"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="워크플로우 이름"
            />
          </div>
          <div>
            <label className="text-xs text-muted-foreground">채널 *</label>
            <select
              className="w-full mt-1 px-3 py-2 border rounded-md text-sm"
              value={form.channelId}
              onChange={(e) => setForm({ ...form, channelId: e.target.value })}
            >
              <option value="">채널 선택</option>
              {channels?.map((ch: any) => (
                <option key={ch.id} value={ch.id}>{ch.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-muted-foreground">유형</label>
            <select
              className="w-full mt-1 px-3 py-2 border rounded-md text-sm"
              value={form.type}
              onChange={(e) => setForm({ ...form, type: e.target.value })}
            >
              <option value="shortform">숏폼</option>
              <option value="longform">롱폼</option>
              <option value="story_shorts">스토리짤</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-muted-foreground">스텝퍼 유형</label>
            <select
              className="w-full mt-1 px-3 py-2 border rounded-md text-sm"
              value={form.stepperType}
              onChange={(e) => setForm({ ...form, stepperType: e.target.value })}
            >
              <option value="tts_based">설명형 (TTS)</option>
              <option value="video_based">스토리형 (AI 영상)</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-muted-foreground">n8n 워크플로우 ID *</label>
            <input
              className="w-full mt-1 px-3 py-2 border rounded-md text-sm"
              value={form.n8nWorkflowId}
              onChange={(e) => setForm({ ...form, n8nWorkflowId: e.target.value })}
              placeholder="예: x6xTzHJ9WbUc94ec"
            />
          </div>
          <div>
            <label className="text-xs text-muted-foreground">Webhook 경로</label>
            <input
              className="w-full mt-1 px-3 py-2 border rounded-md text-sm"
              value={form.webhookPath}
              onChange={(e) => setForm({ ...form, webhookPath: e.target.value })}
              placeholder="예: onca-shortform-v16"
            />
          </div>
          <div className="col-span-2 flex justify-end gap-2 mt-2">
            <Button type="button" variant="outline" size="sm" onClick={onClose}>취소</Button>
            <Button type="submit" size="sm" disabled={submitting}>
              {submitting ? '생성 중...' : '생성'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
