import { config } from '../config';
import type { N8nWorkflow, N8nExecution } from '@n8n-web/shared';

const API_BASE = `${config.n8n.baseUrl}/api/v1`;

async function n8nFetch(endpoint: string, options: RequestInit = {}): Promise<unknown> {
  const url = `${API_BASE}/${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'X-N8N-API-KEY': config.n8n.apiKey,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`n8n API error ${res.status}: ${body}`);
  }

  return res.json();
}

export const n8nClient = {
  async getWorkflows(): Promise<{ data: N8nWorkflow[] }> {
    return n8nFetch('workflows') as Promise<{ data: N8nWorkflow[] }>;
  },

  async getWorkflow(id: string): Promise<N8nWorkflow> {
    return n8nFetch(`workflows/${id}`) as Promise<N8nWorkflow>;
  },

  async updateWorkflow(
    id: string,
    data: { name: string; nodes: unknown[]; connections: unknown; settings?: unknown }
  ): Promise<N8nWorkflow> {
    return n8nFetch(`workflows/${id}`, {
      method: 'PUT',
      body: JSON.stringify({
        ...data,
        settings: data.settings || { executionOrder: 'v1' },
      }),
    }) as Promise<N8nWorkflow>;
  },

  async activateWorkflow(id: string): Promise<N8nWorkflow> {
    return n8nFetch(`workflows/${id}/activate`, {
      method: 'POST',
    }) as Promise<N8nWorkflow>;
  },

  async deactivateWorkflow(id: string): Promise<N8nWorkflow> {
    return n8nFetch(`workflows/${id}/deactivate`, {
      method: 'POST',
    }) as Promise<N8nWorkflow>;
  },

  async getExecutions(workflowId?: string, limit = 20): Promise<{ data: N8nExecution[] }> {
    const params = new URLSearchParams();
    if (workflowId) params.set('workflowId', workflowId);
    params.set('limit', limit.toString());
    return n8nFetch(`executions?${params}`) as Promise<{ data: N8nExecution[] }>;
  },

  async getExecution(id: string): Promise<N8nExecution> {
    return n8nFetch(`executions/${id}`) as Promise<N8nExecution>;
  },

  async retryExecution(id: string): Promise<unknown> {
    return n8nFetch(`executions/${id}/retry`, { method: 'POST' });
  },

  async stopExecution(id: string): Promise<unknown> {
    return n8nFetch(`executions/${id}/stop`, { method: 'POST' });
  },

  async triggerWebhook(webhookPath: string, data?: Record<string, unknown>): Promise<unknown> {
    const url = `${config.n8n.webhookBase}/${webhookPath}`;
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: data ? JSON.stringify(data) : undefined,
    });
    return res.json();
  },
};
