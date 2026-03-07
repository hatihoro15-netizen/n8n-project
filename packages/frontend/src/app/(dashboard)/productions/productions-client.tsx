'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { StatusBadge } from '@/components/status-badge';
import { ProductionProgress } from '@/components/production-progress';
import { VideoPlayer } from '@/components/video-player';
import { useProductions, useWorkflows } from '@/hooks/use-dashboard';
import { api } from '@/lib/api';
import { useQueryClient } from '@tanstack/react-query';
import {
  Plus,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  Clock,
  ExternalLink,
  FileText,
  Square,
  Archive,
  ArchiveRestore,
  Trash2,
  Upload,
  X,
  Loader2,
  Send,
  Film,
  Check,
  Star,
  Eye,
  Image as ImageIcon,
  Video,
  Wand2,
  Sparkles,
  RefreshCw,
  Download,
  Music,
  Volume2,
} from 'lucide-react';
import Link from 'next/link';
import { proxyMediaUrl, downloadViaProxy } from '@/lib/media';

const WEBHOOK_URL = 'https://n8n.srv1345711.hstgr.cloud/webhook/ao-produce';
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

// 나레이션 길이 추정 계수 (한국어 기준, 초당 글자 수)
const NARRATION_CHARS_PER_SEC = 4;
const VIDEO_DURATION_OPTIONS = [0, 10, 20, 30, 40, 50, 60] as const;
type VideoDurationSec = typeof VIDEO_DURATION_OPTIONS[number];

// ── Types ──
type UploadedFile = {
  id: string;
  file: File;
  preview: string;
  type: 'image' | 'video';
  useDirectly: boolean;
  useMode: 'direct' | 'analysis_only';
  autoPrompt: string | null;
  analysis: string | null;
  analyzing: boolean;
  url: string | null;
};

let fileIdCounter = 0;
function nextFileId() { return `file_${++fileIdCounter}_${Date.now()}`; }

// ── Helper: upload files to MinIO via backend ──
async function uploadFilesToMinIO(files: File[]): Promise<string[]> {
  const formData = new FormData();
  files.forEach(f => formData.append('files', f));
  const token = api.getToken();
  const res = await fetch(`${API_BASE}/api/media/upload`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || 'Upload failed');
  }
  const data = await res.json();
  return data.data.urls;
}

// ══════════════════════════════════════════════
// Main Component
// ══════════════════════════════════════════════
export default function ProductionsClient() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [starredFilter, setStarredFilter] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [starredIds, setStarredIds] = useState<Set<string>>(() => {
    if (typeof window === 'undefined') return new Set();
    try {
      const saved = localStorage.getItem('productions_starred');
      return saved ? new Set(JSON.parse(saved)) : new Set();
    } catch { return new Set(); }
  });
  const queryClient = useQueryClient();

  const { data, isLoading } = useProductions({ page, status: statusFilter });
  const allProductions = data?.data;
  const productions = starredFilter
    ? allProductions?.filter((p: any) => starredIds.has(p.id))
    : allProductions;
  const pagination = data?.pagination;

  const toggleStar = (id: string) => {
    setStarredIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      localStorage.setItem('productions_starred', JSON.stringify([...next]));
      return next;
    });
  };

  const toggleSelect = (id: string) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const [showSelectMenu, setShowSelectMenu] = useState(false);

  const selectByStatus = (status?: string) => {
    if (!productions?.length) return;
    const ids = status
      ? productions.filter((p: any) => p.status === status).map((p: any) => p.id)
      : productions.map((p: any) => p.id);
    setSelectedIds(new Set(ids));
    setShowSelectMenu(false);
  };

  const selectStarred = () => {
    if (!productions?.length) return;
    const ids = productions.filter((p: any) => starredIds.has(p.id)).map((p: any) => p.id);
    setSelectedIds(new Set(ids));
    setShowSelectMenu(false);
  };

  const toggleSelectAll = () => {
    if (!productions?.length) return;
    const allIds = productions.map((p: any) => p.id);
    const allSelected = allIds.every((id: string) => selectedIds.has(id));
    if (allSelected) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(allIds));
    }
  };

  const handleBulkDelete = async () => {
    if (selectedIds.size === 0) return;
    if (!confirm(`선택한 ${selectedIds.size}개 항목을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.`)) return;
    for (const id of selectedIds) {
      try { await api.delete(`/api/productions/${id}`); } catch { /* skip */ }
    }
    setSelectedIds(new Set());
    queryClient.invalidateQueries({ queryKey: ['productions'] });
  };

  const handleBulkArchive = async () => {
    if (selectedIds.size === 0) return;
    if (!confirm(`선택한 ${selectedIds.size}개 항목을 보관하시겠습니까?`)) return;
    for (const id of selectedIds) {
      try { await api.patch(`/api/productions/${id}`, { status: 'archived' }); } catch { /* skip */ }
    }
    setSelectedIds(new Set());
    queryClient.invalidateQueries({ queryKey: ['productions'] });
  };

  const statuses = [
    { value: undefined, label: '전체' },
    { value: 'completed', label: '완료' },
    { value: 'failed', label: '실패' },
    { value: 'paused', label: '정지' },
    { value: 'pending', label: '대기' },
    { value: 'archived', label: '보관' },
  ];

  const toggleExpand = (id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  const getVideoUrl = (assets: unknown) => {
    if (!assets || typeof assets !== 'object') return null;
    const a = assets as Record<string, string>;
    const raw = a.videoUrl || a.video_url || a.outputUrl || a.output_url || null;
    return proxyMediaUrl(raw);
  };

  const getThumbnailUrl = (assets: unknown) => {
    if (!assets || typeof assets !== 'object') return null;
    const a = assets as Record<string, string>;
    const raw = a.thumbnailUrl || a.thumbnail_url || null;
    return proxyMediaUrl(raw);
  };

  const getScript = (assets: unknown) => {
    if (!assets || typeof assets !== 'object') return null;
    const a = assets as Record<string, string>;
    return a.script || null;
  };

  return (
    <>
      <Header title="제작 관리" />
      <div className="p-6 space-y-4">
        {/* Actions */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {statuses.map((s) => (
              <Button
                key={s.label}
                variant={!starredFilter && statusFilter === s.value ? 'default' : 'outline'}
                size="sm"
                onClick={() => { setStarredFilter(false); setStatusFilter(s.value); setPage(1); setSelectedIds(new Set()); }}
              >
                {s.label}
              </Button>
            ))}
            <Button
              variant={starredFilter ? 'default' : 'outline'}
              size="sm"
              onClick={() => { setStarredFilter(!starredFilter); setSelectedIds(new Set()); }}
            >
              <Star className={`h-3.5 w-3.5 mr-1 ${starredFilter ? 'fill-current' : ''}`} />
              별표
            </Button>
          </div>
          <div className="flex items-center gap-2">
            <Button onClick={() => setShowForm(!showForm)}>
              {showForm ? <X className="h-4 w-4 mr-2" /> : <Film className="h-4 w-4 mr-2" />}
              {showForm ? '닫기' : '영상 제작'}
            </Button>
            <Link href="/productions/new">
              <Button variant="outline">
                <Plus className="h-4 w-4 mr-2" />
                새 제작
              </Button>
            </Link>
          </div>
        </div>

        {/* Production Form */}
        {showForm && <WhiskProductionForm />}

        {/* Bulk Action Bar */}
        {selectedIds.size > 0 && (
          <div className="flex items-center gap-3 px-4 py-2.5 bg-primary/5 border border-primary/20 rounded-lg">
            <span className="text-sm font-medium">선택 {selectedIds.size}개</span>
            <Button size="sm" variant="outline" onClick={handleBulkArchive}>
              <Archive className="h-3.5 w-3.5 mr-1" />보관
            </Button>
            <Button size="sm" variant="outline" className="text-red-600 hover:text-red-700 hover:bg-red-50" onClick={handleBulkDelete}>
              <Trash2 className="h-3.5 w-3.5 mr-1" />삭제
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setSelectedIds(new Set())}>
              취소
            </Button>
          </div>
        )}

        {/* Production List */}
        <Card>
          <CardContent className="p-0">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="px-2 py-3 w-8 relative">
                    <div className="flex items-center gap-0.5">
                      <input
                        type="checkbox"
                        checked={!!productions?.length && productions.every((p: any) => selectedIds.has(p.id))}
                        onChange={toggleSelectAll}
                        className="h-4 w-4 rounded border-gray-300 accent-primary"
                      />
                      <button
                        onClick={() => setShowSelectMenu(!showSelectMenu)}
                        className="p-0.5 hover:bg-muted rounded"
                      >
                        <ChevronDown className="h-3 w-3 text-muted-foreground" />
                      </button>
                    </div>
                    {showSelectMenu && (
                      <div className="absolute top-full left-0 z-50 mt-1 bg-white border rounded-lg shadow-lg py-1 min-w-[130px]">
                        {[
                          { label: '전체 선택', action: () => selectByStatus() },
                          { label: '완료만', action: () => selectByStatus('completed') },
                          { label: '실패만', action: () => selectByStatus('failed') },
                          { label: '정지만', action: () => selectByStatus('paused') },
                          { label: '대기만', action: () => selectByStatus('pending') },
                          { label: '별표만', action: selectStarred },
                          { label: '선택 해제', action: () => { setSelectedIds(new Set()); setShowSelectMenu(false); } },
                        ].map(item => (
                          <button
                            key={item.label}
                            onClick={item.action}
                            className="w-full text-left px-3 py-1.5 text-sm hover:bg-muted transition-colors"
                          >
                            {item.label}
                          </button>
                        ))}
                      </div>
                    )}
                  </th>
                  <th className="px-2 py-3 w-8" />
                  <th className="px-4 py-3 text-left font-medium w-8" />
                  <th className="px-4 py-3 text-left font-medium">채널</th>
                  <th className="px-4 py-3 text-left font-medium">워크플로우</th>
                  <th className="px-4 py-3 text-left font-medium">제목/주제</th>
                  <th className="px-4 py-3 text-left font-medium">상태</th>
                  <th className="px-4 py-3 text-left font-medium">시작</th>
                  <th className="px-4 py-3 text-left font-medium">완료</th>
                  <th className="px-4 py-3 text-right font-medium w-24">작업</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr>
                    <td colSpan={10} className="px-4 py-8 text-center text-muted-foreground">
                      로딩 중...
                    </td>
                  </tr>
                ) : productions?.length === 0 ? (
                  <tr>
                    <td colSpan={10} className="px-4 py-8 text-center text-muted-foreground">
                      {statusFilter === 'archived' ? '보관된 제작이 없습니다.' : '제작 이력이 없습니다.'}
                    </td>
                  </tr>
                ) : (
                  productions?.map((prod: any) => (
                    <AccordionRow
                      key={prod.id}
                      prod={prod}
                      isExpanded={expandedId === prod.id}
                      onToggle={() => toggleExpand(prod.id)}
                      videoUrl={getVideoUrl(prod.assets)}
                      thumbnailUrl={getThumbnailUrl(prod.assets)}
                      script={getScript(prod.assets)}
                      isSelected={selectedIds.has(prod.id)}
                      onSelect={() => toggleSelect(prod.id)}
                      isStarred={starredIds.has(prod.id)}
                      onToggleStar={() => toggleStar(prod.id)}
                    />
                  ))
                )}
              </tbody>
            </table>
          </CardContent>
        </Card>

        {/* Pagination */}
        {pagination && pagination.totalPages > 1 && (
          <div className="flex items-center justify-center gap-2">
            <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(page - 1)}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm text-muted-foreground">{page} / {pagination.totalPages}</span>
            <Button variant="outline" size="sm" disabled={page === pagination.totalPages} onClick={() => setPage(page + 1)}>
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>
    </>
  );
}

// ══════════════════════════════════════════════
// Production Form (single page, no tabs)
// ══════════════════════════════════════════════
function WhiskProductionForm() {
  const queryClient = useQueryClient();
  const { data: workflowsData } = useWorkflows();
  const workflows = ((workflowsData as any)?.data || []) as any[];

  // Aspect ratio
  const [aspectRatio, setAspectRatio] = useState<'9:16' | '16:9'>('9:16');

  // Mode
  const [productionMode, setProductionMode] = useState<'ai_video' | 'slideshow'>('slideshow');
  const [hasImages, setHasImages] = useState<'yes' | 'no' | null>(null);

  // AI Image Generation (hasImages === 'no')
  const [genPrompt, setGenPrompt] = useState('');
  const [genCount, setGenCount] = useState(4);
  const [generating, setGenerating] = useState(false);
  const [generatedImages, setGeneratedImages] = useState<{ url: string; selected: boolean }[]>([]);
  const [generatedAccepted, setGeneratedAccepted] = useState(false);

  // Slots (통합: 이미지+영상 혼합)
  const [mediaSlots, setMediaSlots] = useState<(UploadedFile | null)[]>([null]);

  // Prompt
  const [promptP1, setPromptP1] = useState('');
  const [showAiPrompt, setShowAiPrompt] = useState(false);
  const [aiPromptLoading, setAiPromptLoading] = useState(false);
  const [aiPromptKo, setAiPromptKo] = useState('');
  const [aiPromptEn, setAiPromptEn] = useState('');
  const [formTopic, setFormTopic] = useState('');
  const [keywords, setKeywords] = useState('');
  const [category, setCategory] = useState('');
  const [videoDurationSec, setVideoDurationSec] = useState<VideoDurationSec>(0);
  const [videoDurationManual, setVideoDurationManual] = useState(false);
  const [engineType, setEngineType] = useState<'character_story' | 'core_message' | 'live_promo' | 'meme' | 'action_sports'>('core_message');
  const [strictMode, setStrictMode] = useState(false);
  const [narrationText, setNarrationText] = useState('');
  const [narrationStyle, setNarrationStyle] = useState('설명형');
  const [narrationTone, setNarrationTone] = useState('차분하게');
  const [imageOrder, setImageOrder] = useState<'auto' | 'sequential'>('auto');
  const [bgmMode, setBgmMode] = useState<'ai_auto' | 'uploaded' | 'none'>('ai_auto');
  const [bgmUrl, setBgmUrl] = useState('');
  const [bgmFileName, setBgmFileName] = useState('');
  const [bgmUploading, setBgmUploading] = useState(false);
  const [sfxMode, setSfxMode] = useState<'ai_auto' | 'uploaded' | 'combined' | 'none'>('ai_auto');
  const [sfxUrl, setSfxUrl] = useState('');
  const [sfxFileName, setSfxFileName] = useState('');
  const [sfxUploading, setSfxUploading] = useState(false);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState('');

  // Form state
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState('');
  const [formSuccess, setFormSuccess] = useState('');

  // Job tracking
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<string | null>(null);
  const [jobVideoUrl, setJobVideoUrl] = useState<string | null>(null);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Auto-import images from /images page via localStorage
  useState(() => {
    if (typeof window === 'undefined') return;
    try {
      const raw = localStorage.getItem('pending_production_images');
      if (!raw) return;
      localStorage.removeItem('pending_production_images');
      const urls: string[] = JSON.parse(raw);
      if (!urls.length) return;
      const slots: (UploadedFile | null)[] = urls.map(url => ({
        id: nextFileId(),
        file: new File([], 'imported.png'),
        preview: url,
        type: 'image' as const,
        useDirectly: true,
        useMode: 'direct' as const,
        autoPrompt: null,
        analysis: null,
        analyzing: false,
        url,
      }));
      setMediaSlots(slots);
      setHasImages('yes');
    } catch { /* ignore */ }
  });

  const maxMediaSlots = 20;
  const filledMediaCount = mediaSlots.filter(s => s !== null).length;
  const showSlots = hasImages === 'yes' || generatedAccepted;

  // ── sessionStorage: 작업 내용 자동 저장/복원 ──
  const DRAFT_KEY = 'ao_production_draft';

  // 복원 (마운트 시 1회)
  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      const raw = sessionStorage.getItem(DRAFT_KEY);
      if (!raw) return;
      const draft = JSON.parse(raw);
      if (draft.promptP1) setPromptP1(draft.promptP1);
      if (draft.formTopic) setFormTopic(draft.formTopic);
      if (draft.keywords) setKeywords(draft.keywords);
      if (draft.category) setCategory(draft.category);
      if (draft.aspectRatio) setAspectRatio(draft.aspectRatio);
      if (draft.productionMode) setProductionMode(draft.productionMode);
      if (draft.engineType) setEngineType(draft.engineType);
      if (draft.strictMode !== undefined) setStrictMode(draft.strictMode);
      if (draft.videoDurationSec !== undefined) setVideoDurationSec(draft.videoDurationSec);
      if (draft.narrationText) setNarrationText(draft.narrationText);
      if (draft.narrationStyle) setNarrationStyle(draft.narrationStyle);
      if (draft.narrationTone) setNarrationTone(draft.narrationTone);
      if (draft.imageOrder) setImageOrder(draft.imageOrder);
      if (draft.hasImages) setHasImages(draft.hasImages);
      if (draft.selectedWorkflowId) setSelectedWorkflowId(draft.selectedWorkflowId);
      if (draft.bgmMode) setBgmMode(draft.bgmMode);
      if (draft.bgmUrl) { setBgmUrl(draft.bgmUrl); setBgmFileName(draft.bgmFileName || ''); }
      if (draft.sfxMode) setSfxMode(draft.sfxMode);
      if (draft.sfxUrl) { setSfxUrl(draft.sfxUrl); setSfxFileName(draft.sfxFileName || ''); }
    } catch { /* ignore */ }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 저장 (입력값 변경 시)
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const draft = {
      promptP1, formTopic, keywords, category,
      aspectRatio, productionMode, engineType, strictMode, videoDurationSec,
      narrationText, narrationStyle, narrationTone, imageOrder,
      hasImages, selectedWorkflowId,
      bgmMode, bgmUrl, bgmFileName, sfxMode, sfxUrl, sfxFileName,
    };
    sessionStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
  }, [promptP1, formTopic, keywords, category, aspectRatio, productionMode, engineType, strictMode, videoDurationSec, narrationText, narrationStyle, narrationTone, imageOrder, hasImages, selectedWorkflowId, bgmMode, bgmUrl, bgmFileName, sfxMode, sfxUrl, sfxFileName]);

  // 나레이션 텍스트 변경 시 → videoDurationSec 자동 계산 (수동 변경 전까지)
  useEffect(() => {
    if (videoDurationManual) return;
    if (!narrationText.trim()) {
      setVideoDurationSec(0);
      return;
    }
    const estimatedSec = Math.ceil(narrationText.trim().length / NARRATION_CHARS_PER_SEC);
    const nearest = [...VIDEO_DURATION_OPTIONS].reverse().find(v => v <= estimatedSec) ?? 0;
    setVideoDurationSec(nearest as VideoDurationSec);
  }, [narrationText, videoDurationManual]);

  const clearDraft = () => sessionStorage.removeItem(DRAFT_KEY);

  // ── Slot handlers ──
  const addSlot = () => {
    setMediaSlots(prev => prev.length < maxMediaSlots ? [...prev, null] : prev);
  };

  const removeSlot = (index: number) => {
    setMediaSlots(prev => {
      const slot = prev[index];
      if (slot) URL.revokeObjectURL(slot.preview);
      return prev.filter((_, i) => i !== index);
    });
  };

  const uploadToSlot = (index: number, file: File) => {
    const isImage = file.type.startsWith('image/');
    const isVideo = file.type.startsWith('video/');
    if (!isImage && !isVideo) return;

    const preview = URL.createObjectURL(file);
    const uf: UploadedFile = {
      id: nextFileId(), file, preview,
      type: isImage ? 'image' : 'video',
      useDirectly: true, useMode: 'direct', autoPrompt: null,
      analysis: null, analyzing: false, url: null,
    };

    setMediaSlots(prev => prev.map((s, i) => i === index ? uf : s));

    if (isImage) {
      analyzeSlotFile(uf.id, uf.file, 'image');
    }
  };

  const changeUseMode = (index: number, mode: 'direct' | 'analysis_only') => {
    setMediaSlots(prev => prev.map((s, i) => {
      if (i !== index || !s) return s;
      return {
        ...s,
        useMode: mode,
        autoPrompt: mode === 'analysis_only' ? (s.autoPrompt || s.analysis || '') : s.autoPrompt,
      };
    }));
    if (mode === 'direct') {
      setProductionMode('ai_video');
    }
  };

  const changeAutoPrompt = (index: number, prompt: string) => {
    setMediaSlots(prev => prev.map((s, i) =>
      i === index && s ? { ...s, autoPrompt: prompt } : s
    ));
  };

  // ── Claude Vision analysis ──
  const analyzeSlotFile = async (fileId: string, file: File, _target: 'image' | 'video') => {
    const updateFile = (updater: (f: UploadedFile) => UploadedFile) => {
      setMediaSlots(prev => prev.map(s => s?.id === fileId ? updater(s) : s));
    };

    updateFile(f => ({ ...f, analyzing: true }));

    try {
      const urls = await uploadFilesToMinIO([file]);
      if (!urls[0]) return;
      updateFile(f => ({ ...f, url: urls[0] }));

      const token = api.getToken();
      const res = await fetch(`${API_BASE}/api/media/analyze-image`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ imageUrl: urls[0] }),
      });

      if (!res.ok) return;
      const data = await res.json();
      if (data.data?.analysis) {
        updateFile(f => ({ ...f, analysis: data.data.analysis, analyzing: false }));
        return;
      }
    } catch {
      // Vision analysis is optional
    }
    updateFile(f => ({ ...f, analyzing: false }));
  };

  // ── AI Image Generation ──
  const handleGenerate = async () => {
    if (!genPrompt.trim()) {
      setFormError('이미지 생성 프롬프트를 입력해주세요.');
      return;
    }
    setGenerating(true);
    setFormError('');
    try {
      const token = api.getToken();
      const res = await fetch(`${API_BASE}/api/media/generate-image`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ prompt: genPrompt, count: genCount, aspect_ratio: aspectRatio }),
      });
      const data = await res.json();
      if (data.data?.images?.length) {
        setGeneratedImages(data.data.images.map((url: string) => ({ url, selected: true })));
      } else {
        setFormError('이미지 생성에 실패했습니다. 다시 시도해주세요.');
      }
    } catch (err) {
      setFormError(err instanceof Error ? err.message : '이미지 생성 실패');
    } finally {
      setGenerating(false);
    }
  };

  const acceptGeneratedImages = () => {
    const selected = generatedImages.filter(img => img.selected);
    if (selected.length === 0) return;
    const newSlots: (UploadedFile | null)[] = selected.map(img => ({
      id: nextFileId(),
      file: new File([], 'generated.png'),
      preview: img.url,
      type: 'image' as const,
      useDirectly: true,
      useMode: 'direct' as const,
      autoPrompt: null,
      analysis: null,
      analyzing: false,
      url: img.url,
    }));
    setMediaSlots(newSlots);
    setGeneratedAccepted(true);
  };

  // Download image
  const [downloadingIdx, setDownloadingIdx] = useState<number | null>(null);
  const handleImageDownload = async (url: string, index: number) => {
    try {
      setDownloadingIdx(index);
      await downloadViaProxy(url, `generated-image-${index + 1}.jpg`);
    } catch { /* ignore */ } finally {
      setDownloadingIdx(null);
    }
  };

  // ── Polling: track job status (2s lightweight) ──
  const startPolling = (productionId: string) => {
    if (pollingRef.current) clearInterval(pollingRef.current);
    setJobId(productionId);
    setJobStatus('started');
    setJobVideoUrl(null);

    pollingRef.current = setInterval(async () => {
      try {
        const res = await api.get(`/api/productions/${productionId}/status`) as { data: any };
        const d = res.data;
        setJobStatus(d.status);

        const videoUrl = d.videoUrl || d.video_url || null;
        if (videoUrl) setJobVideoUrl(proxyMediaUrl(videoUrl));

        if (['completed', 'failed', 'paused'].includes(d.status)) {
          if (pollingRef.current) clearInterval(pollingRef.current);
          pollingRef.current = null;
          queryClient.invalidateQueries({ queryKey: ['productions'] });
        }
      } catch {
        // polling failure, keep trying
      }
    }, 2000);
  };

  // ── Submit ──
  const handleSubmit = async () => {
    if (!selectedWorkflowId) {
      setFormError('워크플로우를 선택해주세요.');
      return;
    }
    if (!promptP1.trim()) {
      setFormError('프롬프트를 입력해주세요.');
      return;
    }
    const isSlideshow = productionMode === 'slideshow';

    const filledMedia = mediaSlots.filter((s): s is UploadedFile => s !== null);

    setSubmitting(true);
    setFormError('');
    setFormSuccess('');

    try {
      const prepareFiles = async (list: UploadedFile[]) => {
        const result: {
          type: 'image' | 'video'; url: string; analysis: string; use_directly: boolean;
          vision_analysis: string; use_mode: string; auto_prompt?: string;
        }[] = [];
        for (const uf of list) {
          let url = uf.url || '';
          if (!url) {
            const urls = await uploadFilesToMinIO([uf.file]);
            url = urls[0] || '';
          }
          if (url) {
            result.push({
              type: uf.type, url,
              analysis: uf.analysis?.trim() || '',
              use_directly: uf.useDirectly,
              vision_analysis: uf.analysis?.trim() || '',
              use_mode: uf.useMode,
              auto_prompt: uf.useMode === 'analysis_only' ? (uf.autoPrompt || uf.analysis || '') : undefined,
            });
          }
        }
        return result;
      };

      // mediaSlots 순서 그대로 payload에 포함
      const files = await prepareFiles(filledMedia);

      const payload: Record<string, unknown> = {
        workflowId: selectedWorkflowId,
        prompt_p1: promptP1.trim(),
        topic: formTopic.trim(),
        keywords: keywords.trim(),
        category: category.trim(),
        aspect_ratio: aspectRatio,
        production_mode: productionMode,
        engine_type: engineType,
        strict_mode: strictMode,
        ...(narrationText.trim() ? { narration_text: narrationText.trim() } : {}),
        narration_style: narrationStyle,
        narration_tone: narrationTone,
        image_order: imageOrder,
        has_images: hasImages === 'yes',
        files,
        bgm_mode: bgmMode,
        sfx_mode: sfxMode,
        ...(bgmUrl ? { bgm_url: bgmUrl } : {}),
        ...(sfxUrl ? { sfx_url: sfxUrl } : {}),
      };

      if (hasImages === 'no' && generatedImages.length > 0) {
        payload.generated_images = generatedImages.filter(img => img.selected).map(img => img.url);
      }

      if (!isSlideshow) {
        payload.duration_sec = videoDurationSec || null;
      }

      const res = await api.post('/api/productions/ao', payload) as { data: any };
      const production = res.data;

      if (production?.id) {
        setFormSuccess('영상 제작이 시작되었습니다!');
        clearDraft();
        startPolling(production.id);
        queryClient.invalidateQueries({ queryKey: ['productions'] });
      } else {
        throw new Error('제작 생성 실패');
      }
    } catch (err) {
      setFormError(err instanceof Error ? err.message : '요청에 실패했습니다.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Card>
      <CardContent className="p-6 space-y-5">
        {/* 1. Workflow selector */}
        <div className="space-y-1.5">
          <label className="text-sm font-medium" htmlFor="workflow_select">
            워크플로우 <span className="text-red-500">*</span>
          </label>
          <select
            id="workflow_select"
            value={selectedWorkflowId}
            onChange={e => setSelectedWorkflowId(e.target.value)}
            className="flex w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          >
            <option value="">워크플로우를 선택하세요</option>
            {workflows.filter((w: any) => w.isActive && w.webhookPath).map((w: any) => (
              <option key={w.id} value={w.id}>
                {w.channel?.name ? `[${w.channel.name}] ` : ''}{w.name}
              </option>
            ))}
          </select>
        </div>

        {/* 2. Aspect ratio */}
        <div>
          <h4 className="text-sm font-medium mb-2">영상 비율</h4>
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => setAspectRatio('9:16')}
              className={`flex items-center justify-center gap-2 p-3 rounded-lg border-2 transition-colors ${
                aspectRatio === '9:16'
                  ? 'border-primary bg-primary/5'
                  : 'border-muted-foreground/20 hover:border-primary/40'
              }`}
            >
              <span className="text-base">📱</span>
              <span className="text-sm font-medium">숏폼 (9:16)</span>
            </button>
            <button
              type="button"
              onClick={() => setAspectRatio('16:9')}
              className={`flex items-center justify-center gap-2 p-3 rounded-lg border-2 transition-colors ${
                aspectRatio === '16:9'
                  ? 'border-primary bg-primary/5'
                  : 'border-muted-foreground/20 hover:border-primary/40'
              }`}
            >
              <span className="text-base">🖥️</span>
              <span className="text-sm font-medium">롱폼 (16:9)</span>
            </button>
          </div>
        </div>

        {/* 3. Production mode */}
        <div>
          <h4 className="text-sm font-medium mb-2">제작 방식</h4>
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => {
                setProductionMode('ai_video');
                setHasImages(null);
                setGeneratedAccepted(false);
                setGeneratedImages([]);
                setMediaSlots([null]);
              }}
              className={`flex flex-col items-start gap-1 p-4 rounded-lg border-2 transition-colors text-left ${
                productionMode === 'ai_video'
                  ? 'border-primary bg-primary/5'
                  : 'border-muted-foreground/20 hover:border-primary/40'
              }`}
            >
              <div className="flex items-center gap-2">
                <Film className="h-4 w-4" />
                <span className="text-sm font-medium">영상화 (Kling AI)</span>
              </div>
              <span className="text-xs text-muted-foreground">이미지를 AI가 분석해서 새 영상 생성</span>
            </button>
            <button
              type="button"
              onClick={() => {
                setProductionMode('slideshow');
                setHasImages(null);
                setGeneratedAccepted(false);
                setGeneratedImages([]);
                setMediaSlots([null]);
              }}
              className={`flex flex-col items-start gap-1 p-4 rounded-lg border-2 transition-colors text-left ${
                productionMode === 'slideshow'
                  ? 'border-primary bg-primary/5'
                  : 'border-muted-foreground/20 hover:border-primary/40'
              }`}
            >
              <div className="flex items-center gap-2">
                <ImageIcon className="h-4 w-4" />
                <span className="text-sm font-medium">슬라이드쇼</span>
              </div>
              <span className="text-xs text-muted-foreground">이미지 그대로 순서대로 이어붙이기</span>
            </button>
          </div>
        </div>

        {/* 3. 이미지가 있나요? */}
        <div>
          <h4 className="text-sm font-medium mb-2">이미지가 있나요?</h4>
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => {
                setHasImages('yes');
                setGeneratedAccepted(false);
                setGeneratedImages([]);
                setMediaSlots([null]);
              }}
              className={`flex flex-col items-center gap-1 p-4 rounded-lg border-2 transition-colors ${
                hasImages === 'yes'
                  ? 'border-emerald-500 bg-emerald-50'
                  : 'border-muted-foreground/20 hover:border-emerald-400'
              }`}
            >
              <Check className="h-5 w-5" />
              <span className="text-sm font-medium">있어요</span>
              <span className="text-xs text-muted-foreground">바로 업로드</span>
            </button>
            <button
              type="button"
              onClick={() => {
                setHasImages('no');
                setGeneratedAccepted(false);
                setGeneratedImages([]);
                setMediaSlots([]);
              }}
              className={`flex flex-col items-center gap-1 p-4 rounded-lg border-2 transition-colors ${
                hasImages === 'no'
                  ? 'border-amber-500 bg-amber-50'
                  : 'border-muted-foreground/20 hover:border-amber-400'
              }`}
            >
              <Wand2 className="h-5 w-5" />
              <span className="text-sm font-medium">없어요</span>
              <span className="text-xs text-muted-foreground">AI로 이미지 생성</span>
            </button>
          </div>
        </div>

        {/* 3-1. Image Order (이미지가 있을 때만 표시) */}
        {hasImages === 'yes' && (
          <div className="space-y-1.5">
            <label className="text-sm font-medium">이미지 순서</label>
            <select
              value={imageOrder}
              onChange={e => setImageOrder(e.target.value as 'auto' | 'sequential')}
              className="flex w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              <option value="auto">자동 (AI가 최적 순서 결정)</option>
              <option value="sequential">순차 (업로드 순서대로)</option>
            </select>
            <p className="text-xs text-muted-foreground">자동: AI가 스토리에 맞게 순서를 재배치합니다. 순차: 업로드한 순서 그대로 사용합니다.</p>
          </div>
        )}

        {/* 4a. AI Image Generation (hasImages === 'no' && not yet accepted) */}
        {hasImages === 'no' && !generatedAccepted && (
          <div className="space-y-3 p-4 rounded-lg border border-amber-200 bg-amber-50/50">
            <h4 className="text-sm font-medium flex items-center gap-1.5">
              <Wand2 className="h-4 w-4 text-amber-600" />
              AI 이미지 생성
            </h4>
            <textarea
              value={genPrompt}
              onChange={e => setGenPrompt(e.target.value)}
              placeholder="생성할 이미지에 대해 설명해주세요"
              rows={3}
              className="flex w-full rounded-md border border-input bg-white px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring resize-y"
            />
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground">생성 수:</span>
                {([2, 4, 6, 8] as const).map(n => (
                  <Button
                    key={n}
                    type="button"
                    variant={genCount === n ? 'default' : 'outline'}
                    size="sm"
                    className="h-7 w-8 text-xs"
                    onClick={() => setGenCount(n)}
                  >
                    {n}
                  </Button>
                ))}
              </div>
              <Button
                type="button"
                onClick={handleGenerate}
                disabled={generating || !genPrompt.trim()}
                size="sm"
              >
                {generating ? (
                  <><Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" />생성 중...</>
                ) : (
                  <><Wand2 className="h-3.5 w-3.5 mr-1" />이미지 생성</>
                )}
              </Button>
            </div>

            {/* Generated images preview */}
            {generatedImages.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">
                    {generatedImages.filter(img => img.selected).length}/{generatedImages.length}개 선택
                  </span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {generatedImages.map((img, i) => (
                    <div key={i} className={`relative aspect-square rounded-lg overflow-hidden border bg-white transition-colors ${img.selected ? 'border-primary ring-1 ring-primary/30' : ''}`}>
                      <img src={img.url} alt={`생성 이미지 ${i + 1}`} className="w-full h-full object-cover" />
                      <label className="absolute top-1.5 left-1.5 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={img.selected}
                          onChange={() => setGeneratedImages(prev => prev.map((g, j) =>
                            j === i ? { ...g, selected: !g.selected } : g
                          ))}
                          className="h-4 w-4 rounded border-gray-300 accent-primary"
                        />
                      </label>
                      <button
                        type="button"
                        onClick={() => handleImageDownload(img.url, i)}
                        disabled={downloadingIdx === i}
                        className="absolute top-1.5 right-1.5 bg-black/50 text-white rounded-full p-1 hover:bg-black/70 transition-colors disabled:opacity-50"
                        title="다운로드"
                      >
                        {downloadingIdx === i ? <Loader2 className="h-3 w-3 animate-spin" /> : <Download className="h-3 w-3" />}
                      </button>
                    </div>
                  ))}
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    type="button"
                    size="sm"
                    onClick={acceptGeneratedImages}
                    disabled={generatedImages.filter(img => img.selected).length === 0}
                  >
                    <Check className="h-3.5 w-3.5 mr-1" />
                    선택한 이미지 사용 ({generatedImages.filter(img => img.selected).length}개)
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={handleGenerate}
                    disabled={generating}
                  >
                    <RefreshCw className={`h-3.5 w-3.5 mr-1 ${generating ? 'animate-spin' : ''}`} />
                    다시 생성
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* 4b. Media slots (hasImages === 'yes' OR generated+accepted) */}
        {showSlots && (
          <div>
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-medium flex items-center gap-1.5">
                <Film className="h-4 w-4" />
                미디어 ({filledMediaCount}/{mediaSlots.length}칸, 최대 {maxMediaSlots}개)
              </h4>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
              {mediaSlots.map((slot, i) => (
                <SlotCard
                  key={slot?.id || `media_empty_${i}`}
                  index={i}
                  slot={slot}
                  slotType="image"
                  onRemove={() => removeSlot(i)}
                  onUpload={(file) => uploadToSlot(i, file)}
                  onChangeUseMode={(mode) => changeUseMode(i, mode)}
                  onChangeAutoPrompt={(prompt) => changeAutoPrompt(i, prompt)}
                />
              ))}
            </div>

            {mediaSlots.length < maxMediaSlots && (
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => addSlot()}
                className="mt-3"
              >
                <Plus className="h-3.5 w-3.5 mr-1" />
                추가 ({mediaSlots.length}/{maxMediaSlots})
              </Button>
            )}
          </div>
        )}

        {/* 7. Prompt fields */}
        <div className="space-y-1.5">
          <label className="text-sm font-medium" htmlFor="prompt_p1">
            프롬프트 <span className="text-red-500">*</span>
          </label>
          <textarea
            id="prompt_p1"
            value={promptP1}
            onChange={e => setPromptP1(e.target.value)}
            placeholder="영상의 방향, 나레이션 내용, 스토리 등을 입력하세요 (필수)"
            rows={3}
            className="flex w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring resize-y"
          />
          {/* AI 추천 프롬프트 생성 버튼 */}
          <button
            type="button"
            onClick={async () => {
              if (showAiPrompt) { setShowAiPrompt(false); return; }
              setShowAiPrompt(true);
              setAiPromptLoading(true);
              setAiPromptKo('');
              setAiPromptEn('');
              try {
                const token = api.getToken();
                const res = await fetch(`${API_BASE}/api/productions/suggest-prompt`, {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { Authorization: `Bearer ${token}` } : {}),
                  },
                  body: JSON.stringify({
                    prompt_p1: promptP1.trim(),
                    narration_text: narrationText.trim() || undefined,
                    duration_sec: videoDurationSec || undefined,
                  }),
                });
                const data = await res.json();
                if (data.success && data.data) {
                  setAiPromptKo(data.data.korean || '');
                  setAiPromptEn(data.data.english || '');
                } else {
                  setAiPromptKo(`오류: ${data.message || 'API 호출 실패'}`);
                }
              } catch (err) {
                setAiPromptKo(`오류: ${err instanceof Error ? err.message : '네트워크 오류'}`);
              }
              setAiPromptLoading(false);
            }}
            className="flex items-center gap-1.5 text-sm text-violet-600 hover:text-violet-700 transition-colors mt-1"
          >
            <Sparkles className="h-3.5 w-3.5" />
            {showAiPrompt ? 'AI 추천 닫기' : 'AI 추천 프롬프트 생성'}
          </button>
          {/* AI 추천 결과 영역 */}
          {showAiPrompt && (
            <div className="space-y-3 p-4 rounded-lg border border-violet-200 bg-violet-50/50 mt-2">
              <h4 className="text-sm font-medium flex items-center gap-1.5">
                <Sparkles className="h-4 w-4 text-violet-600" />
                AI 추천 프롬프트
              </h4>
              {aiPromptLoading ? (
                <div className="flex items-center gap-2 py-4 justify-center text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  프롬프트 생성 중...
                </div>
              ) : (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div className="space-y-1.5">
                      <label className="text-xs text-muted-foreground">한글판</label>
                      <textarea
                        value={aiPromptKo}
                        onChange={e => setAiPromptKo(e.target.value)}
                        rows={4}
                        className="flex w-full rounded-md border border-input bg-white px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring resize-y"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-xs text-muted-foreground">영문판</label>
                      <textarea
                        value={aiPromptEn}
                        onChange={e => setAiPromptEn(e.target.value)}
                        rows={4}
                        className="flex w-full rounded-md border border-input bg-white px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring resize-y"
                      />
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => { setPromptP1(aiPromptEn); setShowAiPrompt(false); }}
                      disabled={!aiPromptEn.trim()}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-violet-600 text-white text-sm hover:bg-violet-700 disabled:opacity-50 transition-colors"
                    >
                      <Check className="h-3.5 w-3.5" />
                      영문 프롬프트로 확정
                    </button>
                    <button
                      type="button"
                      onClick={() => { setPromptP1(aiPromptKo); setShowAiPrompt(false); }}
                      disabled={!aiPromptKo.trim()}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-violet-300 text-violet-700 text-sm hover:bg-violet-100 disabled:opacity-50 transition-colors"
                    >
                      <Check className="h-3.5 w-3.5" />
                      한글판으로 확정
                    </button>
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        {/* 7-0. Duration + Engine Type + Strict Mode */}
        <div className={`grid grid-cols-1 ${productionMode === 'ai_video' ? 'sm:grid-cols-3' : ''} gap-4`}>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">영상 길이</label>
            <select
              value={videoDurationSec}
              onChange={e => {
                setVideoDurationSec(Number(e.target.value) as VideoDurationSec);
                setVideoDurationManual(true);
              }}
              className="flex w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              {VIDEO_DURATION_OPTIONS.map(v => (
                <option key={v} value={v}>{v === 0 ? '자동 (AI 판단)' : `${v}초`}</option>
              ))}
            </select>
            {narrationText.trim() && !videoDurationManual && (
              <p className="text-xs text-muted-foreground mt-1">
                나레이션 {narrationText.trim().length}자 → 약 {Math.ceil(narrationText.trim().length / NARRATION_CHARS_PER_SEC)}초 추정
              </p>
            )}
          </div>
          {productionMode === 'ai_video' && (
            <>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">엔진 타입</label>
                <select
                  value={engineType}
                  onChange={e => setEngineType(e.target.value as typeof engineType)}
                  className="flex w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                >
                  <option value="character_story">캐릭터 스토리</option>
                  <option value="core_message">핵심 메시지</option>
                  <option value="live_promo">라이브 프로모</option>
                  <option value="meme">밈</option>
                  <option value="action_sports">액션/스포츠</option>
                </select>
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">길이 엄격 모드</label>
                <label className="flex items-center gap-2 cursor-pointer h-9 px-3">
                  <input type="checkbox" checked={strictMode} onChange={e => setStrictMode(e.target.checked)} className="rounded" />
                  <span className="text-sm text-muted-foreground">strict (목표 길이 ±1초)</span>
                </label>
              </div>
            </>
          )}
        </div>

        {/* 7-1. Narration */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium">나레이션</h4>
          <div className="space-y-1.5">
            <label className="text-xs text-muted-foreground">나레이션 텍스트 (선택 — 비워두면 AI가 자동 생성)</label>
            <textarea
              value={narrationText}
              onChange={e => setNarrationText(e.target.value)}
              placeholder="직접 나레이션을 작성하거나, 비워두면 프롬프트 기반으로 AI가 자동 생성합니다"
              rows={3}
              className="flex w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring resize-y"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-xs text-muted-foreground">나레이션 스타일</label>
              <select
                value={narrationStyle}
                onChange={e => setNarrationStyle(e.target.value)}
                className="flex w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              >
                <option value="설명형">설명형</option>
                <option value="스토리형">스토리형</option>
                <option value="광고형">광고형</option>
                <option value="감성형">감성형</option>
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-xs text-muted-foreground">나레이션 톤</label>
              <select
                value={narrationTone}
                onChange={e => setNarrationTone(e.target.value)}
                className="flex w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              >
                <option value="차분하게">차분하게</option>
                <option value="흥분되게">흥분되게</option>
                <option value="유머러스하게">유머러스하게</option>
                <option value="긴박하게">긴박하게</option>
              </select>
            </div>
          </div>
        </div>

        {/* 7-2. BGM / 효과음 모드 선택 + 업로드 */}
        <div className="space-y-4">
          <h4 className="text-sm font-medium">오디오</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* BGM */}
            <div className="space-y-2">
              <label className="text-xs text-muted-foreground flex items-center gap-1"><Music className="h-3.5 w-3.5" />BGM (배경음악)</label>
              <div className="flex flex-wrap gap-2">
                {(['ai_auto', 'uploaded', 'none'] as const).map(mode => {
                  const disabled = mode === 'uploaded' && !bgmUrl;
                  const labels: Record<string, string> = { ai_auto: 'AI 자동 추천', uploaded: '내가 올린 것만', none: '사용 안함' };
                  const icons: Record<string, string> = { ai_auto: '🤖', uploaded: '📁', none: '❌' };
                  return (
                    <button
                      key={mode}
                      type="button"
                      disabled={disabled}
                      onClick={() => setBgmMode(mode)}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md border text-sm transition-colors ${
                        bgmMode === mode
                          ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                          : disabled
                            ? 'border-muted-foreground/10 text-muted-foreground/40 cursor-not-allowed'
                            : 'border-muted-foreground/20 hover:border-emerald-400 cursor-pointer'
                      }`}
                    >
                      <span>{icons[mode]}</span>
                      <span>{labels[mode]}</span>
                    </button>
                  );
                })}
              </div>
              {/* BGM 파일 업로드 */}
              <div className="mt-1">
                {bgmUrl ? (
                  <div className="flex items-center gap-2 text-sm bg-muted/50 border rounded-md px-3 py-2">
                    <Music className="h-4 w-4 text-emerald-600" />
                    <span className="truncate max-w-[180px]">{bgmFileName || 'BGM 업로드됨'}</span>
                    <button onClick={() => { setBgmUrl(''); setBgmFileName(''); if (bgmMode === 'uploaded') setBgmMode('ai_auto'); }} className="ml-auto text-muted-foreground hover:text-destructive"><X className="h-3 w-3" /></button>
                  </div>
                ) : (
                  <label className="flex items-center gap-2 text-sm border border-dashed rounded-md px-4 py-2 cursor-pointer hover:bg-muted/30 transition-colors">
                    {bgmUploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
                    {bgmUploading ? '업로드 중...' : 'mp3/wav 파일 선택'}
                    <input
                      type="file"
                      accept="audio/mpeg,audio/wav,.mp3,.wav"
                      className="hidden"
                      onChange={async (e) => {
                        const file = e.target.files?.[0];
                        if (!file) return;
                        setBgmUploading(true);
                        try {
                          const token = api.getToken();
                          const fd = new FormData();
                          fd.append('file', file);
                          const res = await fetch(`${API_BASE}/api/media/upload`, {
                            method: 'POST',
                            headers: token ? { Authorization: `Bearer ${token}` } : {},
                            body: fd,
                          });
                          const data = await res.json();
                          if (data.data?.urls?.[0]) {
                            setBgmUrl(data.data.urls[0]);
                            setBgmFileName(file.name);
                            setBgmMode('uploaded');
                          }
                        } catch { /* ignore */ }
                        setBgmUploading(false);
                      }}
                    />
                  </label>
                )}
              </div>
            </div>
            {/* SFX */}
            <div className="space-y-2">
              <label className="text-xs text-muted-foreground flex items-center gap-1"><Volume2 className="h-3.5 w-3.5" />효과음</label>
              <div className="flex flex-wrap gap-2">
                {(['ai_auto', 'uploaded', 'combined', 'none'] as const).map(mode => {
                  const needsFile = mode === 'uploaded' || mode === 'combined';
                  const disabled = needsFile && !sfxUrl;
                  const labels: Record<string, string> = { ai_auto: 'AI 자동 추천', uploaded: '내가 올린 것만', combined: '합쳐서', none: '사용 안함' };
                  const icons: Record<string, string> = { ai_auto: '🤖', uploaded: '📁', combined: '📁🤖', none: '❌' };
                  return (
                    <button
                      key={mode}
                      type="button"
                      disabled={disabled}
                      onClick={() => setSfxMode(mode)}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md border text-sm transition-colors ${
                        sfxMode === mode
                          ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                          : disabled
                            ? 'border-muted-foreground/10 text-muted-foreground/40 cursor-not-allowed'
                            : 'border-muted-foreground/20 hover:border-emerald-400 cursor-pointer'
                      }`}
                    >
                      <span>{icons[mode]}</span>
                      <span>{labels[mode]}</span>
                    </button>
                  );
                })}
              </div>
              {/* SFX 파일 업로드 */}
              <div className="mt-1">
                {sfxUrl ? (
                  <div className="flex items-center gap-2 text-sm bg-muted/50 border rounded-md px-3 py-2">
                    <Volume2 className="h-4 w-4 text-emerald-600" />
                    <span className="truncate max-w-[180px]">{sfxFileName || '효과음 업로드됨'}</span>
                    <button onClick={() => { setSfxUrl(''); setSfxFileName(''); if (sfxMode === 'uploaded' || sfxMode === 'combined') setSfxMode('ai_auto'); }} className="ml-auto text-muted-foreground hover:text-destructive"><X className="h-3 w-3" /></button>
                  </div>
                ) : (
                  <label className="flex items-center gap-2 text-sm border border-dashed rounded-md px-4 py-2 cursor-pointer hover:bg-muted/30 transition-colors">
                    {sfxUploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
                    {sfxUploading ? '업로드 중...' : 'mp3/wav 파일 선택'}
                    <input
                      type="file"
                      accept="audio/mpeg,audio/wav,.mp3,.wav"
                      className="hidden"
                      onChange={async (e) => {
                        const file = e.target.files?.[0];
                        if (!file) return;
                        setSfxUploading(true);
                        try {
                          const token = api.getToken();
                          const fd = new FormData();
                          fd.append('file', file);
                          const res = await fetch(`${API_BASE}/api/media/upload`, {
                            method: 'POST',
                            headers: token ? { Authorization: `Bearer ${token}` } : {},
                            body: fd,
                          });
                          const data = await res.json();
                          if (data.data?.urls?.[0]) {
                            setSfxUrl(data.data.urls[0]);
                            setSfxFileName(file.name);
                            setSfxMode('uploaded');
                          }
                        } catch { /* ignore */ }
                        setSfxUploading(false);
                      }}
                    />
                  </label>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* 메타데이터 (접기/펴기) */}
        <details className="group">
          <summary className="text-sm font-medium cursor-pointer text-muted-foreground hover:text-foreground flex items-center gap-1.5">
            <ChevronRight className="h-3.5 w-3.5 group-open:rotate-90 transition-transform" />
            메타데이터 (표시용 — 영상 생성에 영향 없음)
          </summary>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-2 pl-5">
            <div className="space-y-1.5">
              <label className="text-xs text-muted-foreground" htmlFor="form_topic">주제</label>
              <Input id="form_topic" value={formTopic} onChange={e => setFormTopic(e.target.value)} placeholder="예: 역사 미스터리" />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs text-muted-foreground" htmlFor="form_keywords">키워드</label>
              <Input id="form_keywords" value={keywords} onChange={e => setKeywords(e.target.value)} placeholder="쉼표 구분" />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs text-muted-foreground" htmlFor="form_category">카테고리</label>
              <Input id="form_category" value={category} onChange={e => setCategory(e.target.value)} placeholder="예: entertainment" />
            </div>
          </div>
        </details>

        {/* Error / Success */}
        {formError && <p className="text-sm text-destructive">{formError}</p>}
        {formSuccess && <p className="text-sm text-emerald-600">{formSuccess}</p>}

        {/* 8. Submit */}
        <div className="flex items-center gap-3">
          <Button onClick={handleSubmit} disabled={submitting || !selectedWorkflowId || !promptP1.trim() || !!jobId}>
            {submitting ? (
              <><Loader2 className="h-4 w-4 mr-2 animate-spin" />처리 중...</>
            ) : (
              <><Send className="h-4 w-4 mr-2" />영상 제작 시작</>
            )}
          </Button>
          <span className="text-xs text-muted-foreground">
            {showSlots && filledMediaCount > 0
              ? `미디어 ${filledMediaCount}개 → ${productionMode === 'slideshow' ? '슬라이드쇼' : '영상'} 제작`
              : '프롬프트 기반으로 영상 제작'}
          </span>
        </div>

        {/* 9. Job Status Tracker */}
        {jobId && (
          <div className="mt-4 p-4 rounded-lg border bg-muted/30 space-y-3">
            <div className="flex items-center gap-3">
              <h4 className="text-sm font-medium">제작 상태</h4>
              <JobStatusBadge status={jobStatus} />
            </div>

            {/* Progress bar */}
            <JobProgressBar status={jobStatus} />

            {jobVideoUrl && (
              <div>
                <p className="text-xs text-muted-foreground mb-2">영상 미리보기</p>
                <video
                  src={jobVideoUrl}
                  controls
                  className="w-full max-w-md rounded-lg border"
                  preload="metadata"
                />
              </div>
            )}
            <div className="flex items-center gap-2">
              {jobStatus === 'completed' && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => { setJobId(null); setJobStatus(null); setJobVideoUrl(null); }}
                >
                  새 제작 시작
                </Button>
              )}
              {jobStatus === 'failed' && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={async () => {
                    try {
                      await api.post(`/api/productions/${jobId}/retry`);
                      setJobStatus('started');
                      startPolling(jobId);
                    } catch (err: any) {
                      setFormError(err.message || '재시도 실패');
                    }
                  }}
                >
                  <RefreshCw className="h-3.5 w-3.5 mr-1" />
                  재시도
                </Button>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ══════════════════════════════════════════════
// Job Status Badge
// ══════════════════════════════════════════════
const JOB_STATUS_MAP: Record<string, { label: string; color: string }> = {
  pending: { label: '대기 중', color: 'bg-gray-100 text-gray-700' },
  started: { label: '제작 중...', color: 'bg-blue-100 text-blue-700' },
  script_ready: { label: '스크립트 완료', color: 'bg-blue-100 text-blue-700' },
  tts_ready: { label: 'TTS 완료', color: 'bg-blue-100 text-blue-700' },
  images_ready: { label: '이미지 완료', color: 'bg-blue-100 text-blue-700' },
  videos_ready: { label: '영상 클립 완료', color: 'bg-blue-100 text-blue-700' },
  rendering: { label: '렌더링 중...', color: 'bg-purple-100 text-purple-700' },
  uploading: { label: '업로드 중...', color: 'bg-amber-100 text-amber-700' },
  completed: { label: '완료', color: 'bg-emerald-100 text-emerald-700' },
  failed: { label: '실패', color: 'bg-red-100 text-red-700' },
  paused: { label: '정지', color: 'bg-gray-100 text-gray-700' },
};

function JobStatusBadge({ status }: { status: string | null }) {
  if (!status) return null;
  const info = JOB_STATUS_MAP[status] || { label: status, color: 'bg-gray-100 text-gray-700' };
  const isActive = ['started', 'script_ready', 'tts_ready', 'images_ready', 'videos_ready', 'rendering', 'uploading'].includes(status);
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${info.color}`}>
      {isActive && <Loader2 className="h-3 w-3 animate-spin" />}
      {info.label}
    </span>
  );
}

// ══════════════════════════════════════════════
// Job Progress Bar
// ══════════════════════════════════════════════
const STATUS_PERCENT: Record<string, number> = {
  pending: 0,
  started: 10,
  script_ready: 25,
  tts_ready: 40,
  images_ready: 55,
  videos_ready: 70,
  rendering: 85,
  uploading: 95,
  completed: 100,
  failed: 0,
  paused: 0,
};

function JobProgressBar({ status }: { status: string | null }) {
  if (!status || status === 'failed' || status === 'paused') return null;
  const pct = STATUS_PERCENT[status] ?? 0;
  const isComplete = status === 'completed';

  return (
    <div className="space-y-1">
      <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            isComplete ? 'bg-emerald-500' : 'bg-primary'
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="text-xs text-muted-foreground">{pct}%</p>
    </div>
  );
}

// ══════════════════════════════════════════════
// Slot Card (unified for image + video)
// ══════════════════════════════════════════════
function SlotCard({
  index,
  slot,
  slotType,
  onRemove,
  onUpload,
  onChangeUseMode,
  onChangeAutoPrompt,
}: {
  index: number;
  slot: UploadedFile | null;
  slotType: 'image' | 'video';
  onRemove: () => void;
  onUpload: (file: File) => void;
  onChangeUseMode?: (mode: 'direct' | 'analysis_only') => void;
  onChangeAutoPrompt?: (prompt: string) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const acceptType = slotType === 'image' ? 'image/*,video/*' : 'video/*';

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (!file) return;
    const isImage = file.type.startsWith('image/');
    const isVideo = file.type.startsWith('video/');
    if (slotType === 'image' && !isImage && !isVideo) return;
    if (slotType === 'video' && !isVideo) return;
    onUpload(file);
  };

  const dragProps = {
    onDragOver: (e: React.DragEvent) => { e.preventDefault(); setDragging(true); },
    onDragLeave: () => setDragging(false),
    onDrop: handleDrop,
  };

  if (!slot) {
    return (
      <div
        {...dragProps}
        className={`relative border-2 border-dashed rounded-lg flex flex-col items-center justify-center min-h-[140px] transition-colors ${
          dragging ? 'border-primary bg-primary/5' : 'border-muted-foreground/20 hover:border-primary/40'
        }`}
      >
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="flex flex-col items-center gap-1.5 text-muted-foreground p-4"
        >
          <Upload className="h-5 w-5" />
          <span className="text-xs">{slotType === 'image' ? '이미지 추가' : '영상 추가'}</span>
        </button>
        <input
          ref={inputRef}
          type="file"
          accept={acceptType}
          className="hidden"
          onChange={e => {
            if (e.target.files?.[0]) onUpload(e.target.files[0]);
            e.target.value = '';
          }}
        />
        <button
          type="button"
          onClick={onRemove}
          className="absolute top-1 right-1 text-muted-foreground/40 hover:text-red-500 transition-colors"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      </div>
    );
  }

  const isImage = slot.type === 'image';

  return (
    <div {...dragProps} className={`relative border rounded-lg overflow-hidden bg-white group ${dragging ? 'ring-2 ring-primary' : ''}`}>
      {/* Preview */}
      <div className="relative aspect-video bg-muted/30">
        {isImage ? (
          <img src={slot.preview} alt={`${slotType} ${index + 1}`} className="w-full h-full object-cover" />
        ) : (
          <video src={slot.preview} className="w-full h-full object-cover" autoPlay muted loop playsInline />
        )}
        <div className="absolute top-0 left-0 bg-black/50 text-white text-xs px-1.5 py-0.5 rounded-br flex items-center gap-1">
          {isImage ? <ImageIcon className="h-3 w-3" /> : <><span>🎬</span><Video className="h-3 w-3" /></>}
          {index + 1}
        </div>
        <button
          type="button"
          onClick={onRemove}
          className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <X className="h-3 w-3" />
        </button>
        {slot.analyzing && (
          <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
            <Loader2 className="h-5 w-5 text-white animate-spin" />
          </div>
        )}
      </div>

      {/* Use mode radio options (image slots only) */}
      {isImage && onChangeUseMode && (
        <div className="p-2 space-y-1 text-xs">
          {([
            { value: 'direct' as const, label: '직접 사용', icon: Eye },
            { value: 'analysis_only' as const, label: '분석만 반영', icon: FileText },
          ]).map(opt => (
            <label
              key={opt.value}
              className={`flex items-center gap-1.5 p-1 rounded cursor-pointer transition-colors ${
                slot.useMode === opt.value ? 'bg-primary/10 text-primary font-medium' : 'hover:bg-muted'
              }`}
            >
              <input
                type="radio"
                name={`useMode_${slot.id}`}
                checked={slot.useMode === opt.value}
                onChange={() => onChangeUseMode(opt.value)}
                className="h-3 w-3 accent-primary"
              />
              <opt.icon className="h-3 w-3" />
              {opt.label}
            </label>
          ))}

          {/* Analysis result preview (direct mode) */}
          {slot.analysis && slot.useMode === 'direct' && (
            <p className="text-[10px] text-muted-foreground line-clamp-2 mt-1 px-1">{slot.analysis}</p>
          )}

          {/* Auto prompt (analysis_only mode): Vision 분석 기반 프롬프트 자동 생성 → 수정 가능 */}
          {slot.useMode === 'analysis_only' && onChangeAutoPrompt && (
            <div className="mt-1 space-y-1">
              <p className="text-[10px] text-muted-foreground px-1">Vision 분석 기반 프롬프트 (수정 가능)</p>
              <textarea
                value={slot.autoPrompt || ''}
                onChange={e => onChangeAutoPrompt(e.target.value)}
                placeholder={slot.analyzing ? '분석 중...' : '분석 완료 후 자동 입력됩니다'}
                rows={3}
                className="w-full rounded border border-input bg-transparent px-2 py-1 text-xs shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring resize-y"
              />
            </div>
          )}
        </div>
      )}

      {/* Video: simple info */}
      {!isImage && (
        <div className="p-2 text-xs text-muted-foreground">
          <p className="truncate">{slot.file.name || '영상'}</p>
        </div>
      )}
    </div>
  );
}

// ══════════════════════════════════════════════
// AccordionRow
// ══════════════════════════════════════════════
function AccordionRow({
  prod,
  isExpanded,
  onToggle,
  videoUrl,
  thumbnailUrl,
  script,
  isSelected,
  onSelect,
  isStarred,
  onToggleStar,
}: {
  prod: any;
  isExpanded: boolean;
  onToggle: () => void;
  videoUrl: string | null;
  thumbnailUrl: string | null;
  script: string | null;
  isSelected: boolean;
  onSelect: () => void;
  isStarred: boolean;
  onToggleStar: () => void;
}) {
  const [aborting, setAborting] = useState(false);
  const [archiving, setArchiving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const queryClient = useQueryClient();
  const isInProgress = !['completed', 'failed', 'paused', 'archived'].includes(prod.status);
  const canArchive = ['completed', 'failed', 'paused'].includes(prod.status);
  const isArchived = prod.status === 'archived';
  const canDelete = ['completed', 'failed', 'paused', 'pending', 'archived'].includes(prod.status);

  const handleAbort = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('이 제작을 중단하시겠습니까?')) return;
    setAborting(true);
    try {
      await api.patch(`/api/productions/${prod.id}`, { status: 'failed', errorMessage: '사용자 중단' });
      queryClient.invalidateQueries({ queryKey: ['productions'] });
    } catch { /* noop */ } finally { setAborting(false); }
  };

  const handleArchive = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('이 제작을 보관하시겠습니까?')) return;
    setArchiving(true);
    try {
      await api.patch(`/api/productions/${prod.id}`, { status: 'archived' });
      queryClient.invalidateQueries({ queryKey: ['productions'] });
    } catch { /* noop */ } finally { setArchiving(false); }
  };

  const handleRestore = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setArchiving(true);
    try {
      await api.patch(`/api/productions/${prod.id}`, { status: 'restore' });
      queryClient.invalidateQueries({ queryKey: ['productions'] });
    } catch { /* noop */ } finally { setArchiving(false); }
  };

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (isInProgress) { alert('진행중인 제작은 삭제할 수 없습니다. 먼저 중단하세요.'); return; }
    if (!confirm('이 제작을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) return;
    setDeleting(true);
    try {
      await api.delete(`/api/productions/${prod.id}`);
      queryClient.invalidateQueries({ queryKey: ['productions'] });
    } catch (err: any) { alert(err.message || '삭제에 실패했습니다.'); } finally { setDeleting(false); }
  };

  return (
    <>
      <tr
        className={`border-b hover:bg-muted/50 cursor-pointer select-none transition-colors ${isExpanded ? 'bg-muted/30' : ''} ${isSelected ? 'bg-primary/5' : ''}`}
        onClick={onToggle}
      >
        <td className="px-2 py-3" onClick={e => e.stopPropagation()}>
          <input
            type="checkbox"
            checked={isSelected}
            onChange={onSelect}
            className="h-4 w-4 rounded border-gray-300 accent-primary"
          />
        </td>
        <td className="px-2 py-3" onClick={e => e.stopPropagation()}>
          <button onClick={onToggleStar} className="p-0.5 hover:scale-110 transition-transform">
            <Star className={`h-4 w-4 ${isStarred ? 'fill-yellow-400 text-yellow-400' : 'text-muted-foreground/30 hover:text-yellow-400'}`} />
          </button>
        </td>
        <td className="px-4 py-3">
          <ChevronDown className={`h-4 w-4 text-muted-foreground transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`} />
        </td>
        <td className="px-4 py-3"><Badge variant="outline">{prod.channel?.name}</Badge></td>
        <td className="px-4 py-3 text-muted-foreground">{prod.workflow?.name}</td>
        <td className="px-4 py-3">
          {prod.title || prod.topic ? (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-primary/5 border border-primary/10 font-medium text-sm text-foreground">
              <FileText className="h-3.5 w-3.5 text-primary/60" />
              {prod.title || prod.topic}
            </span>
          ) : <span className="text-muted-foreground/50">-</span>}
        </td>
        <td className="px-4 py-3">
          <div className="flex items-center gap-2">
            <StatusBadge status={prod.status} />
            {isInProgress && (
              <button onClick={handleAbort} disabled={aborting} className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs font-medium text-red-600 hover:bg-red-50 transition-colors" title="제작 중단">
                <Square className="h-3 w-3" />{aborting ? '...' : '중단'}
              </button>
            )}
          </div>
        </td>
        <td className="px-4 py-3 text-muted-foreground text-xs">{prod.startedAt ? new Date(prod.startedAt).toLocaleString('ko-KR') : '-'}</td>
        <td className="px-4 py-3 text-muted-foreground text-xs">{prod.completedAt ? new Date(prod.completedAt).toLocaleString('ko-KR') : '-'}</td>
        <td className="px-4 py-3 text-right">
          <div className="flex items-center justify-end gap-1">
            {isArchived ? (
              <button onClick={handleRestore} disabled={archiving} className="p-1.5 rounded-md text-muted-foreground/50 hover:text-blue-600 hover:bg-blue-50 transition-colors" title="꺼내기 (복원)">
                <ArchiveRestore className="h-4 w-4" />
              </button>
            ) : canArchive ? (
              <button onClick={handleArchive} disabled={archiving} className="p-1.5 rounded-md text-muted-foreground/50 hover:text-amber-600 hover:bg-amber-50 transition-colors" title="보관">
                <Archive className="h-4 w-4" />
              </button>
            ) : null}
            {canDelete && (
              <button onClick={handleDelete} disabled={deleting} className="p-1.5 rounded-md text-muted-foreground/50 hover:text-red-600 hover:bg-red-50 transition-colors" title="삭제">
                <Trash2 className="h-4 w-4" />
              </button>
            )}
          </div>
        </td>
      </tr>
      {isExpanded && (
        <tr className="border-b bg-muted/10">
          <td colSpan={10} className="px-6 py-5">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-1">
                {videoUrl ? (
                  <VideoPlayer src={videoUrl} poster={thumbnailUrl || undefined} title={prod.title || prod.topic || undefined} className="max-w-[240px]" />
                ) : (
                  <div className="flex items-center justify-center aspect-[9/16] max-w-[240px] mx-auto rounded-xl bg-muted/50 border border-dashed border-muted-foreground/20">
                    <div className="text-center text-muted-foreground/50">
                      <FileText className="h-8 w-8 mx-auto mb-2" /><p className="text-xs">영상 없음</p>
                    </div>
                  </div>
                )}
              </div>
              <div className="lg:col-span-2 space-y-4">
                <div>
                  <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">진행 상황</h4>
                  <ProductionProgress status={prod.status} stepperType={prod.workflow?.stepperType || 'tts_based'} />
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">제작 정보</h4>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
                    <div className="space-y-0.5"><span className="text-xs text-muted-foreground">채널</span><p className="font-medium">{prod.channel?.name || '-'}</p></div>
                    <div className="space-y-0.5"><span className="text-xs text-muted-foreground">워크플로우</span><p className="font-medium">{prod.workflow?.name || '-'}</p></div>
                    <div className="space-y-0.5"><span className="text-xs text-muted-foreground">주제</span><p className="font-medium">{prod.topic || '-'}</p></div>
                  </div>
                  <div className="flex flex-wrap gap-4 mt-3 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1"><Clock className="h-3 w-3" />생성: {new Date(prod.createdAt).toLocaleString('ko-KR')}</div>
                    {prod.startedAt && <div className="flex items-center gap-1"><Clock className="h-3 w-3" />시작: {new Date(prod.startedAt).toLocaleString('ko-KR')}</div>}
                    {prod.completedAt && <div className="flex items-center gap-1"><Clock className="h-3 w-3" />완료: {new Date(prod.completedAt).toLocaleString('ko-KR')}</div>}
                    {prod.startedAt && prod.completedAt && (
                      <div className="flex items-center gap-1 text-emerald-600 font-medium">
                        <Clock className="h-3 w-3" />소요: {Math.round((new Date(prod.completedAt).getTime() - new Date(prod.startedAt).getTime()) / 1000)}초
                      </div>
                    )}
                  </div>
                  {prod.youtubeUrl && (
                    <a href={prod.youtubeUrl} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 mt-3 text-sm text-blue-600 hover:text-blue-800" onClick={e => e.stopPropagation()}>
                      <ExternalLink className="h-3.5 w-3.5" />YouTube에서 보기
                    </a>
                  )}
                </div>
                {script && (
                  <div>
                    <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">스크립트</h4>
                    <pre className="text-xs bg-muted/60 p-3 rounded-lg overflow-auto max-h-48 whitespace-pre-wrap border">{script}</pre>
                  </div>
                )}
                {prod.errorMessage && (
                  <div>
                    {prod.errorMessage.includes('타임아웃') ? (
                      <>
                        <h4 className="text-xs font-semibold text-amber-600 uppercase tracking-wider mb-2 flex items-center gap-1.5"><Clock className="h-3.5 w-3.5" />응답 시간 초과</h4>
                        <pre className="text-xs bg-amber-50 text-amber-800 p-3 rounded-lg overflow-auto max-h-32 whitespace-pre-wrap border border-amber-200">{prod.errorMessage}</pre>
                      </>
                    ) : (
                      <>
                        <h4 className="text-xs font-semibold text-red-600 uppercase tracking-wider mb-2">에러</h4>
                        <pre className="text-xs bg-red-50 text-red-800 p-3 rounded-lg overflow-auto max-h-32 whitespace-pre-wrap border border-red-200">{prod.errorMessage}</pre>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  );
}
