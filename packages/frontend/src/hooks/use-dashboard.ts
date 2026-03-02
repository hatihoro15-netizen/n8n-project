import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import type { DashboardStats, Production, Workflow, Channel } from '@n8n-web/shared';

export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: () =>
      api.get<{
        success: boolean;
        data: DashboardStats & { recentProductions: Production[] };
      }>('/api/dashboard/stats'),
    refetchInterval: 30000,
  });
}

export function useChannels() {
  return useQuery({
    queryKey: ['channels'],
    queryFn: () =>
      api.get<{
        success: boolean;
        data: (Channel & { workflows: Workflow[]; _count: { productions: number } })[];
      }>('/api/channels'),
  });
}

export function useChannel(id: string) {
  return useQuery({
    queryKey: ['channels', id],
    queryFn: () =>
      api.get<{ success: boolean; data: Channel & { workflows: Workflow[]; productions: Production[] } }>(
        `/api/channels/${id}`
      ),
    enabled: !!id,
  });
}

export function useWorkflows() {
  return useQuery({
    queryKey: ['workflows'],
    queryFn: () =>
      api.get<{
        success: boolean;
        data: (Workflow & { channel: Channel; _count: { productions: number; prompts: number } })[];
      }>('/api/workflows'),
  });
}

export function useWorkflow(id: string) {
  return useQuery({
    queryKey: ['workflows', id],
    queryFn: () =>
      api.get<{ success: boolean; data: Workflow }>(`/api/workflows/${id}`),
    enabled: !!id,
  });
}

export function useProductions(params?: { channelId?: string; status?: string; page?: number }) {
  const searchParams = new URLSearchParams();
  if (params?.channelId) searchParams.set('channelId', params.channelId);
  if (params?.status) searchParams.set('status', params.status);
  if (params?.page) searchParams.set('page', params.page.toString());

  return useQuery({
    queryKey: ['productions', params],
    queryFn: () =>
      api.get<{
        success: boolean;
        data: Production[];
        pagination: { page: number; limit: number; total: number; totalPages: number };
      }>(`/api/productions?${searchParams}`),
    refetchInterval: 10000,
  });
}

export function useProduction(id: string) {
  return useQuery({
    queryKey: ['productions', id],
    queryFn: () =>
      api.get<{
        success: boolean;
        data: Production & { workflow: Workflow & { channel: Channel }; channel: Channel };
      }>(`/api/productions/${id}`),
    enabled: !!id,
    refetchInterval: (query) => {
      const status = query.state.data?.data?.status;
      if (status && !['completed', 'failed', 'paused', 'archived'].includes(status)) {
        return 3000;
      }
      return false;
    },
  });
}

export function useCharacters() {
  return useQuery({
    queryKey: ['characters'],
    queryFn: () =>
      api.get<{ success: boolean; data: unknown[] }>('/api/characters'),
  });
}
