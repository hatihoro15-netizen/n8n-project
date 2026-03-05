// ============================================================
// Shared Types for n8n-web platform
// ============================================================

// --- Channel ---
export interface Channel {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  youtubeChannelId: string | null;
  thumbnailUrl: string | null;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

// --- Workflow ---
export type WorkflowType = 'shortform' | 'longform' | 'story_shorts' | 'ao';

export interface Workflow {
  id: string;
  channelId: string;
  n8nWorkflowId: string;
  name: string;
  type: WorkflowType;
  webhookPath: string | null;
  webhookUrl: string | null;
  scheduleExpression: string | null;
  stepperType: string;
  isActive: boolean;
  channel?: Channel;
  createdAt: string;
  updatedAt: string;
}

// --- Character ---
export interface Character {
  id: string;
  name: string;
  nameKo: string;
  personality: string | null;
  speechStyle: string | null;
  voiceId: string | null;
  voiceSettings: Record<string, unknown> | null;
  imageUrl: string | null;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

// --- Prompt ---
export interface Prompt {
  id: string;
  workflowId: string;
  nodeName: string;
  content: string;
  version: number;
  isDeployed: boolean;
  deployedAt: string | null;
  workflow?: Workflow;
  createdAt: string;
  updatedAt: string;
}

// --- Production ---
export type ProductionStatus =
  | 'pending'
  | 'started'
  | 'script_ready'
  | 'tts_ready'
  | 'images_ready'
  | 'videos_ready'
  | 'rendering'
  | 'uploading'
  | 'completed'
  | 'failed'
  | 'paused'
  | 'archived';

export type StepperType = 'tts_based' | 'video_based';

export interface Production {
  id: string;
  workflowId: string;
  channelId: string;
  title: string | null;
  topic: string | null;
  status: ProductionStatus;
  previousStatus: ProductionStatus | null;
  n8nExecutionId: string | null;
  assets: Record<string, unknown> | null;
  youtubeVideoId: string | null;
  youtubeUrl: string | null;
  errorMessage: string | null;
  cost: number | null;
  workflow?: Workflow;
  channel?: Channel;
  startedAt: string | null;
  completedAt: string | null;
  createdAt: string;
  updatedAt: string;
}

// --- Analytics ---
export interface Analytics {
  id: string;
  productionId: string | null;
  channelId: string;
  youtubeVideoId: string;
  title: string;
  views: number;
  likes: number;
  comments: number;
  ctr: number | null;
  avgWatchDuration: number | null;
  recordedAt: string;
  createdAt: string;
}

// --- API Response Types ---
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// --- Dashboard Stats ---
export interface DashboardStats {
  totalProductions: number;
  completedToday: number;
  failedToday: number;
  activeProductions: number;
  channelStats: {
    channelId: string;
    channelName: string;
    totalProductions: number;
    lastProductionAt: string | null;
  }[];
}

// --- Auth ---
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: {
    id: string;
    username: string;
  };
}

// --- Production Trigger ---
export interface TriggerProductionRequest {
  workflowId: string;
  topic?: string;
  characterIds?: string[];
}

// --- N8n Types ---
export interface N8nWorkflow {
  id: string;
  name: string;
  active: boolean;
  nodes: N8nNode[];
  connections: Record<string, unknown>;
}

export interface N8nNode {
  name: string;
  type: string;
  parameters: Record<string, unknown>;
  position: [number, number];
  id: string;
}

export interface N8nExecution {
  id: string;
  finished: boolean;
  mode: string;
  startedAt: string;
  stoppedAt: string | null;
  status: string;
  workflowId: string;
}
