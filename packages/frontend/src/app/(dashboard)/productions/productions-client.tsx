'use client';

import { useState, useRef, useCallback } from 'react';
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
  Timer,
  Star,
  Eye,
  EyeOff,
  Image as ImageIcon,
  Video,
} from 'lucide-react';
import Link from 'next/link';
import { proxyMediaUrl } from '@/lib/media';

const WEBHOOK_URL = 'https://n8n.srv1345711.hstgr.cloud/webhook/ao-produce';
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

// ── Types ──
type UploadedFile = {
  id: string;
  file: File;
  preview: string;
  type: 'image' | 'video';
  useDirectly: boolean; // true = "유" (use directly), false = "무" (analyze only)
  analysis: string | null;
  analyzing: boolean;
  url: string | null; // MinIO uploaded URL
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

        {/* Whisk-style Production Form */}
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
// Whisk Production Form (2-step: Upload → Prompt)
// ══════════════════════════════════════════════
function WhiskProductionForm() {
  const [activeTab, setActiveTab] = useState<'upload' | 'prompt'>('upload');
  const queryClient = useQueryClient();
  const { data: workflowsData } = useWorkflows();
  const workflows = ((workflowsData as any)?.data || []) as any[];
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Step 1: Uploaded files
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);

  // Step 2: Prompt fields
  const [promptP1, setPromptP1] = useState('');
  const [formTopic, setFormTopic] = useState('');
  const [keywords, setKeywords] = useState('');
  const [category, setCategory] = useState('');
  const [clipDuration, setClipDuration] = useState<5 | 8>(5);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string>('');

  // Form state
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState('');
  const [formSuccess, setFormSuccess] = useState('');

  // Job tracking
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<string | null>(null);
  const [jobVideoUrl, setJobVideoUrl] = useState<string | null>(null);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const imageCount = uploadedFiles.filter(f => f.type === 'image').length;
  const videoCount = uploadedFiles.filter(f => f.type === 'video').length;

  // ── Add files ──
  const addFiles = useCallback((fileList: FileList | File[]) => {
    const newFiles: UploadedFile[] = [];
    for (const file of Array.from(fileList)) {
      const isImage = file.type.startsWith('image/');
      const isVideo = file.type.startsWith('video/');
      if (!isImage && !isVideo) continue;

      const preview = URL.createObjectURL(file);
      const uf: UploadedFile = {
        id: nextFileId(),
        file,
        preview,
        type: isImage ? 'image' : 'video',
        useDirectly: true, // default: "유" (use directly)
        analysis: null,
        analyzing: false,
        url: null,
      };
      newFiles.push(uf);
    }

    setUploadedFiles(prev => [...prev, ...newFiles]);

    // Auto-analyze images
    for (const uf of newFiles) {
      if (uf.type === 'image') {
        analyzeFile(uf.id, uf.file);
      }
    }
  }, []);

  const removeFile = (id: string) => {
    setUploadedFiles(prev => {
      const file = prev.find(f => f.id === id);
      if (file) URL.revokeObjectURL(file.preview);
      return prev.filter(f => f.id !== id);
    });
  };

  const toggleUseDirectly = (id: string) => {
    setUploadedFiles(prev => prev.map(f =>
      f.id === id ? { ...f, useDirectly: !f.useDirectly } : f
    ));
  };

  // ── Claude Vision analysis ──
  const analyzeFile = async (fileId: string, file: File) => {
    setUploadedFiles(prev => prev.map(f =>
      f.id === fileId ? { ...f, analyzing: true } : f
    ));

    try {
      const urls = await uploadFilesToMinIO([file]);
      if (!urls[0]) return;

      // Save uploaded URL
      setUploadedFiles(prev => prev.map(f =>
        f.id === fileId ? { ...f, url: urls[0] } : f
      ));

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
        setUploadedFiles(prev => prev.map(f =>
          f.id === fileId ? { ...f, analysis: data.data.analysis, analyzing: false } : f
        ));
        return;
      }
    } catch {
      // Vision analysis is optional
    }
    setUploadedFiles(prev => prev.map(f =>
      f.id === fileId ? { ...f, analyzing: false } : f
    ));
  };

  // ── Drag and drop ──
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    addFiles(e.dataTransfer.files);
  }, [addFiles]);

  // ── Polling: track job status ──
  const startPolling = (productionId: string) => {
    if (pollingRef.current) clearInterval(pollingRef.current);
    setJobId(productionId);
    setJobStatus('started');
    setJobVideoUrl(null);

    pollingRef.current = setInterval(async () => {
      try {
        const res = await api.get(`/api/productions/${productionId}`) as { data: any };
        const prod = res.data;
        setJobStatus(prod.status);

        const assets = prod.assets as Record<string, string> | null;
        const videoUrl = assets?.videoUrl || assets?.video_url || assets?.rendered_video_url || null;
        if (videoUrl) setJobVideoUrl(proxyMediaUrl(videoUrl));

        if (['completed', 'failed', 'paused'].includes(prod.status)) {
          if (pollingRef.current) clearInterval(pollingRef.current);
          pollingRef.current = null;
          queryClient.invalidateQueries({ queryKey: ['productions'] });
        }
      } catch {
        // polling failure, keep trying
      }
    }, 10000);
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
    if (uploadedFiles.length === 0) {
      setFormError('파일을 1개 이상 추가해주세요.');
      return;
    }

    setSubmitting(true);
    setFormError('');
    setFormSuccess('');

    try {
      // Upload files that don't have URLs yet
      const files: {
        type: 'image' | 'video';
        url: string;
        analysis: string;
        use_directly: boolean;
      }[] = [];

      for (const uf of uploadedFiles) {
        let url = uf.url || '';
        if (!url) {
          const urls = await uploadFilesToMinIO([uf.file]);
          url = urls[0] || '';
        }
        if (url) {
          files.push({
            type: uf.type,
            url,
            analysis: uf.analysis?.trim() || '',
            use_directly: uf.useDirectly,
          });
        }
      }

      const payload = {
        workflowId: selectedWorkflowId,
        prompt_p1: promptP1.trim(),
        topic: formTopic.trim() || undefined,
        keywords: keywords.trim() || undefined,
        category: category.trim() || undefined,
        clip_duration: clipDuration,
        files,
      };

      const res = await api.post('/api/productions/ao', payload) as { data: any };
      const production = res.data;

      if (production?.id) {
        setFormSuccess('영상 제작이 시작되었습니다!');
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
      <CardContent className="p-0">
        {/* Tab Headers */}
        <div className="flex border-b">
          <button
            type="button"
            onClick={() => setActiveTab('upload')}
            className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'upload'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <Upload className="h-4 w-4" />
            Step 1. 파일 업로드
            {uploadedFiles.length > 0 && (
              <Badge variant="secondary" className="ml-1 text-xs">{uploadedFiles.length}</Badge>
            )}
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('prompt')}
            className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'prompt'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <Film className="h-4 w-4" />
            Step 2. 프롬프트 & 제작
          </button>
        </div>

        <div className="p-6">
          {/* ── STEP 1: File Upload ── */}
          {activeTab === 'upload' && (
            <div className="space-y-5">
              {/* Drop zone */}
              <div
                onDragOver={e => e.preventDefault()}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-muted-foreground/25 rounded-xl p-8 text-center cursor-pointer hover:border-primary/50 hover:bg-primary/5 transition-colors"
              >
                <Upload className="h-8 w-8 mx-auto text-muted-foreground/40 mb-3" />
                <p className="text-sm font-medium text-muted-foreground">
                  이미지 또는 영상 파일을 드래그하거나 클릭하여 추가
                </p>
                <p className="text-xs text-muted-foreground/60 mt-1">
                  JPG, PNG, WebP, MP4, MOV 등 지원
                </p>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*,video/*"
                multiple
                className="hidden"
                onChange={e => {
                  if (e.target.files) addFiles(e.target.files);
                  e.target.value = '';
                }}
              />

              {/* File summary */}
              {uploadedFiles.length > 0 && (
                <div className="flex items-center gap-3 text-sm text-muted-foreground">
                  <span className="font-medium text-foreground">{uploadedFiles.length}개 파일</span>
                  {imageCount > 0 && (
                    <span className="flex items-center gap-1">
                      <ImageIcon className="h-3.5 w-3.5" /> 이미지 {imageCount}
                    </span>
                  )}
                  {videoCount > 0 && (
                    <span className="flex items-center gap-1">
                      <Video className="h-3.5 w-3.5" /> 영상 {videoCount}
                    </span>
                  )}
                </div>
              )}

              {/* File cards grid */}
              {uploadedFiles.length > 0 && (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
                  {uploadedFiles.map((uf, i) => (
                    <FileCard
                      key={uf.id}
                      index={i}
                      file={uf}
                      onRemove={() => removeFile(uf.id)}
                      onToggleUse={() => toggleUseDirectly(uf.id)}
                    />
                  ))}
                </div>
              )}

              {/* Next step hint */}
              {uploadedFiles.length > 0 && (
                <div className="flex justify-end">
                  <Button onClick={() => setActiveTab('prompt')}>
                    Step 2로 이동
                    <ChevronRight className="h-4 w-4 ml-1" />
                  </Button>
                </div>
              )}
            </div>
          )}

          {/* ── STEP 2: Prompt & Production ── */}
          {activeTab === 'prompt' && (
            <div className="space-y-5">
              {/* Main prompt */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium" htmlFor="prompt_p1">
                  메인 프롬프트 <span className="text-red-500">*</span>
                </label>
                <textarea
                  id="prompt_p1"
                  value={promptP1}
                  onChange={e => setPromptP1(e.target.value)}
                  placeholder="영상 제작 프롬프트를 입력하세요 (P1)"
                  rows={3}
                  className="flex w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring resize-y"
                />
              </div>

              {/* Workflow selector */}
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

              {/* Clip duration + file count summary */}
              <div className="flex items-center gap-4">
                <div>
                  <h4 className="text-sm font-medium mb-2">클립 길이</h4>
                  <div className="flex gap-2">
                    {([5, 8] as const).map(d => (
                      <Button
                        key={d}
                        type="button"
                        variant={clipDuration === d ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setClipDuration(d)}
                      >
                        <Timer className="h-3.5 w-3.5 mr-1" />
                        {d}초
                      </Button>
                    ))}
                  </div>
                </div>
                {uploadedFiles.length > 0 && (
                  <div className="flex items-center gap-2 px-4 py-2 bg-primary/5 rounded-lg border border-primary/10">
                    <Film className="h-4 w-4 text-primary/60" />
                    <span className="text-sm font-medium">
                      {uploadedFiles.length}개 파일 업로드됨
                      {imageCount > 0 && ` (이미지 ${imageCount}`}
                      {videoCount > 0 && `, 영상 ${videoCount}`}
                      {(imageCount > 0 || videoCount > 0) && ')'}
                    </span>
                  </div>
                )}
              </div>

              {/* Topic / Keywords / Category */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium" htmlFor="form_topic">주제</label>
                  <Input id="form_topic" value={formTopic} onChange={e => setFormTopic(e.target.value)} placeholder="예: 역사 미스터리" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium" htmlFor="form_keywords">키워드</label>
                  <Input id="form_keywords" value={keywords} onChange={e => setKeywords(e.target.value)} placeholder="쉼표 구분" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium" htmlFor="form_category">카테고리</label>
                  <Input id="form_category" value={category} onChange={e => setCategory(e.target.value)} placeholder="예: entertainment" />
                </div>
              </div>

              {/* Error / Success */}
              {formError && <p className="text-sm text-destructive">{formError}</p>}
              {formSuccess && <p className="text-sm text-emerald-600">{formSuccess}</p>}

              {/* Submit */}
              <div className="flex items-center gap-3">
                <Button onClick={handleSubmit} disabled={submitting || uploadedFiles.length === 0 || !selectedWorkflowId || !!jobId}>
                  {submitting ? (
                    <><Loader2 className="h-4 w-4 mr-2 animate-spin" />처리 중...</>
                  ) : (
                    <><Send className="h-4 w-4 mr-2" />영상 제작 시작</>
                  )}
                </Button>
                <span className="text-xs text-muted-foreground">
                  {uploadedFiles.length > 0
                    ? `${uploadedFiles.length}개 파일 → 제작 시작`
                    : '파일을 1개 이상 추가해주세요 (Step 1)'}
                </span>
              </div>

              {/* Job Status Tracker */}
              {jobId && (
                <div className="mt-4 p-4 rounded-lg border bg-muted/30 space-y-3">
                  <div className="flex items-center gap-3">
                    <h4 className="text-sm font-medium">제작 상태</h4>
                    <JobStatusBadge status={jobStatus} />
                  </div>
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
                  {jobStatus === 'completed' && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => { setJobId(null); setJobStatus(null); setJobVideoUrl(null); }}
                    >
                      새 제작 시작
                    </Button>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
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
// File Card (upload grid item with use/analyze toggle)
// ══════════════════════════════════════════════
function FileCard({
  index,
  file,
  onRemove,
  onToggleUse,
}: {
  index: number;
  file: UploadedFile;
  onRemove: () => void;
  onToggleUse: () => void;
}) {
  const isImage = file.type === 'image';

  return (
    <div className="space-y-1.5">
      <div className="relative group aspect-square rounded-lg overflow-hidden border bg-muted/30">
        {isImage ? (
          <img src={file.preview} alt={`파일 ${index + 1}`} className="w-full h-full object-cover" />
        ) : (
          <video src={file.preview} className="w-full h-full object-cover" muted preload="metadata" />
        )}

        {/* Index badge */}
        <div className="absolute top-0 left-0 bg-black/50 text-white text-xs px-1.5 py-0.5 rounded-br flex items-center gap-1">
          {isImage ? <ImageIcon className="h-3 w-3" /> : <Video className="h-3 w-3" />}
          {index + 1}
        </div>

        {/* Remove button */}
        <button
          type="button"
          onClick={onRemove}
          className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <X className="h-3 w-3" />
        </button>

        {/* Analysis overlay */}
        {file.analyzing && (
          <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
            <Loader2 className="h-5 w-5 text-white animate-spin" />
          </div>
        )}
        {file.analysis && !file.analyzing && (
          <div className="absolute bottom-0 left-0 right-0 bg-black/60 text-white text-[10px] p-1.5 line-clamp-2">
            {file.analysis}
          </div>
        )}
      </div>

      {/* Use directly toggle */}
      <button
        type="button"
        onClick={onToggleUse}
        className={`w-full flex items-center justify-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium transition-colors ${
          file.useDirectly
            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100'
            : 'bg-amber-50 text-amber-700 border border-amber-200 hover:bg-amber-100'
        }`}
      >
        {file.useDirectly ? (
          <><Eye className="h-3 w-3" />유 (직접 사용)</>
        ) : (
          <><EyeOff className="h-3 w-3" />무 (분석만)</>
        )}
      </button>
    </div>
  );
}

// ══════════════════════════════════════════════
// AccordionRow (unchanged)
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
