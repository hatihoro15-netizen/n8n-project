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
import { useProductions } from '@/hooks/use-dashboard';
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
  ImagePlus,
  X,
  Loader2,
  Send,
  Sparkles,
  Film,
  User,
  Mountain,
  Palette,
  RefreshCw,
  Check,
  Timer,
} from 'lucide-react';
import Link from 'next/link';
import { proxyMediaUrl } from '@/lib/media';

const WEBHOOK_URL = 'https://n8n.srv1345711.hstgr.cloud/webhook/ao-produce';
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

// ── Types ──
type Slot = {
  file: File | null;
  preview: string | null;
  prompt: string;
  analysis: string | null;
  includeAudio: boolean;
};

type RefImage = { file: File | null; preview: string | null };

const EMPTY_SLOT: Slot = { file: null, preview: null, prompt: '', analysis: null, includeAudio: false };
const EMPTY_REF: RefImage = { file: null, preview: null };

function createSlots(): Slot[] {
  return Array.from({ length: 10 }, () => ({ ...EMPTY_SLOT }));
}

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
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  const { data, isLoading } = useProductions({ page, status: statusFilter });
  const productions = data?.data;
  const pagination = data?.pagination;

  const statuses = [
    { value: undefined, label: '전체' },
    { value: 'pending', label: '대기' },
    { value: 'started', label: '시작됨' },
    { value: 'completed', label: '완료' },
    { value: 'failed', label: '실패' },
    { value: 'paused', label: '정지' },
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
                variant={statusFilter === s.value ? 'default' : 'outline'}
                size="sm"
                onClick={() => { setStatusFilter(s.value); setPage(1); }}
              >
                {s.label}
              </Button>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <Button onClick={() => setShowForm(!showForm)}>
              {showForm ? <X className="h-4 w-4 mr-2" /> : <Sparkles className="h-4 w-4 mr-2" />}
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

        {/* Production List */}
        <Card>
          <CardContent className="p-0">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50">
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
                    <td colSpan={8} className="px-4 py-8 text-center text-muted-foreground">
                      로딩 중...
                    </td>
                  </tr>
                ) : productions?.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-4 py-8 text-center text-muted-foreground">
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
// Whisk Production Form (2-tab)
// ══════════════════════════════════════════════
function WhiskProductionForm() {
  const [activeTab, setActiveTab] = useState<'generate' | 'video'>('generate');

  // Common form fields
  const [promptP1, setPromptP1] = useState('');
  const [formTopic, setFormTopic] = useState('');
  const [keywords, setKeywords] = useState('');
  const [category, setCategory] = useState('');
  const [clipDuration, setClipDuration] = useState<5 | 8>(5);

  // Step 1: Reference images
  const [refImages, setRefImages] = useState<{ subject: RefImage; scene: RefImage; style: RefImage }>({
    subject: { ...EMPTY_REF },
    scene: { ...EMPTY_REF },
    style: { ...EMPTY_REF },
  });
  const [generateCount, setGenerateCount] = useState<1 | 2 | 3>(2);
  const [generatedImages, setGeneratedImages] = useState<string[]>([]);
  const [generating, setGenerating] = useState(false);
  const [genError, setGenError] = useState('');

  // Step 2: Slots
  const [slots, setSlots] = useState<Slot[]>(createSlots);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState('');
  const [formSuccess, setFormSuccess] = useState('');

  const filledSlots = slots.filter(s => s.file || s.preview);
  const estimatedLength = filledSlots.length * clipDuration;

  // ── Ref image handlers ──
  const setRefImage = (key: 'subject' | 'scene' | 'style', file: File) => {
    const preview = URL.createObjectURL(file);
    setRefImages(prev => {
      if (prev[key].preview) URL.revokeObjectURL(prev[key].preview!);
      return { ...prev, [key]: { file, preview } };
    });
  };

  const removeRefImage = (key: 'subject' | 'scene' | 'style') => {
    setRefImages(prev => {
      if (prev[key].preview) URL.revokeObjectURL(prev[key].preview!);
      return { ...prev, [key]: { ...EMPTY_REF } };
    });
  };

  // ── AI image generation ──
  const handleGenerate = async () => {
    if (!promptP1.trim()) {
      setGenError('프롬프트를 입력해주세요.');
      return;
    }
    setGenerating(true);
    setGenError('');

    try {
      // Upload ref images to MinIO first
      const refUrls: Record<string, string> = {};
      for (const [key, ref] of Object.entries(refImages)) {
        if (ref.file) {
          const urls = await uploadFilesToMinIO([ref.file]);
          if (urls[0]) refUrls[key] = urls[0];
        }
      }

      const token = api.getToken();
      const res = await fetch(`${API_BASE}/api/media/generate-image`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          prompt: promptP1.trim(),
          count: generateCount,
          ref_subject: refUrls.subject,
          ref_scene: refUrls.scene,
          ref_style: refUrls.style,
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.message || `생성 실패 (${res.status})`);
      }

      const data = await res.json();
      setGeneratedImages(data.data.images || []);
    } catch (err) {
      setGenError(err instanceof Error ? err.message : '이미지 생성에 실패했습니다.');
    } finally {
      setGenerating(false);
    }
  };

  // ── Use generated image → add to first empty slot ──
  const useGeneratedImage = (imageUrl: string) => {
    setSlots(prev => {
      const next = [...prev];
      const emptyIdx = next.findIndex(s => !s.file && !s.preview);
      if (emptyIdx === -1) return prev;
      next[emptyIdx] = { ...next[emptyIdx], preview: imageUrl, file: null };
      return next;
    });
    setActiveTab('video');
  };

  // ── Slot file drop/click ──
  const addFileToSlot = (index: number, file: File) => {
    const preview = URL.createObjectURL(file);
    setSlots(prev => {
      const next = [...prev];
      if (next[index].preview && next[index].file) URL.revokeObjectURL(next[index].preview!);
      next[index] = { ...next[index], file, preview };
      return next;
    });
    // Trigger vision analysis
    analyzeSlotImage(index, file);
  };

  const removeSlot = (index: number) => {
    setSlots(prev => {
      const next = [...prev];
      if (next[index].preview && next[index].file) URL.revokeObjectURL(next[index].preview!);
      next[index] = { ...EMPTY_SLOT };
      return next;
    });
  };

  const setSlotPrompt = (index: number, prompt: string) => {
    setSlots(prev => {
      const next = [...prev];
      next[index] = { ...next[index], prompt };
      return next;
    });
  };

  const setSlotIncludeAudio = (index: number, includeAudio: boolean) => {
    setSlots(prev => {
      const next = [...prev];
      next[index] = { ...next[index], includeAudio };
      return next;
    });
  };

  // ── Claude Vision analysis ──
  const analyzeSlotImage = async (index: number, file: File) => {
    try {
      const urls = await uploadFilesToMinIO([file]);
      if (!urls[0]) return;

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
        setSlots(prev => {
          const next = [...prev];
          next[index] = { ...next[index], analysis: data.data.analysis };
          return next;
        });
      }
    } catch {
      // Vision analysis is optional, silently fail
    }
  };

  // ── Submit: upload slot images → webhook ──
  const handleSubmit = async () => {
    if (!promptP1.trim()) {
      setFormError('프롬프트를 입력해주세요.');
      return;
    }
    if (filledSlots.length === 0) {
      setFormError('이미지를 1장 이상 추가해주세요.');
      return;
    }

    setSubmitting(true);
    setFormError('');
    setFormSuccess('');

    try {
      // Upload local files to MinIO (skip already-uploaded URLs)
      const clips: {
        image_url: string;
        vision_analysis: string;
        scene_prompt: string;
        include_audio: boolean;
      }[] = [];

      for (const slot of slots) {
        if (!slot.file && !slot.preview) continue;

        let imageUrl = slot.preview || '';
        if (slot.file) {
          const urls = await uploadFilesToMinIO([slot.file]);
          imageUrl = urls[0] || '';
        }

        if (imageUrl) {
          clips.push({
            image_url: imageUrl,
            vision_analysis: slot.analysis?.trim() || '',
            scene_prompt: slot.prompt?.trim() || '',
            include_audio: slot.includeAudio,
          });
        }
      }

      const payload = {
        prompt_p1: promptP1.trim(),
        topic: formTopic.trim() || undefined,
        keywords: keywords.trim() || undefined,
        category: category.trim() || undefined,
        clip_duration: clipDuration,
        clips,
      };

      const webhookRes = await fetch(WEBHOOK_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!webhookRes.ok) {
        throw new Error(`웹훅 호출 실패 (${webhookRes.status})`);
      }

      setFormSuccess('영상 제작이 시작되었습니다!');
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
            onClick={() => setActiveTab('generate')}
            className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'generate'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <Sparkles className="h-4 w-4" />
            Step 1. 이미지 생성
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('video')}
            className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'video'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <Film className="h-4 w-4" />
            Step 2. 영상 생성
            {filledSlots.length > 0 && (
              <Badge variant="secondary" className="ml-1 text-xs">{filledSlots.length}</Badge>
            )}
          </button>
        </div>

        <div className="p-6">
          {/* Common: Main prompt */}
          <div className="space-y-1.5 mb-4">
            <label className="text-sm font-medium" htmlFor="prompt_p1">
              메인 프롬프트 <span className="text-red-500">*</span>
            </label>
            <textarea
              id="prompt_p1"
              value={promptP1}
              onChange={e => setPromptP1(e.target.value)}
              placeholder="이미지 생성 프롬프트를 입력하세요"
              rows={3}
              className="flex w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring resize-y"
            />
          </div>

          {/* ── STEP 1: Image Generation ── */}
          {activeTab === 'generate' && (
            <div className="space-y-5">
              {/* Reference Images */}
              <div>
                <h4 className="text-sm font-medium mb-3">참고 이미지 (선택)</h4>
                <div className="grid grid-cols-3 gap-4">
                  {([
                    { key: 'subject' as const, label: '피사체', icon: User },
                    { key: 'scene' as const, label: '장면', icon: Mountain },
                    { key: 'style' as const, label: '스타일', icon: Palette },
                  ]).map(({ key, label, icon: Icon }) => (
                    <RefImageSlot
                      key={key}
                      label={label}
                      icon={<Icon className="h-6 w-6" />}
                      preview={refImages[key].preview}
                      onFile={(f) => setRefImage(key, f)}
                      onRemove={() => removeRefImage(key)}
                    />
                  ))}
                </div>
              </div>

              {/* Generate count */}
              <div>
                <h4 className="text-sm font-medium mb-2">생성 개수</h4>
                <div className="flex gap-2">
                  {([1, 2, 3] as const).map(n => (
                    <Button
                      key={n}
                      type="button"
                      variant={generateCount === n ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setGenerateCount(n)}
                    >
                      {n}개
                    </Button>
                  ))}
                </div>
              </div>

              {/* Generate button */}
              <Button onClick={handleGenerate} disabled={generating || !promptP1.trim()}>
                {generating ? (
                  <><Loader2 className="h-4 w-4 mr-2 animate-spin" />생성 중...</>
                ) : (
                  <><Sparkles className="h-4 w-4 mr-2" />이미지 생성</>
                )}
              </Button>

              {genError && <p className="text-sm text-destructive">{genError}</p>}

              {/* Generated results grid */}
              {generatedImages.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium mb-3">생성 결과</h4>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                    {generatedImages.map((url, i) => (
                      <div key={i} className="border rounded-lg overflow-hidden">
                        <img src={url} alt={`생성 ${i + 1}`} className="w-full aspect-square object-cover" />
                        <div className="flex gap-1 p-2">
                          <Button
                            size="sm"
                            variant="default"
                            className="flex-1 text-xs"
                            onClick={() => useGeneratedImage(url)}
                          >
                            <Check className="h-3 w-3 mr-1" />사용
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="flex-1 text-xs"
                            onClick={handleGenerate}
                            disabled={generating}
                          >
                            <RefreshCw className="h-3 w-3 mr-1" />재생성
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ── STEP 2: Video Generation ── */}
          {activeTab === 'video' && (
            <div className="space-y-5">
              {/* Clip duration + estimated length */}
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
                {filledSlots.length > 0 && (
                  <div className="flex items-center gap-2 px-4 py-2 bg-primary/5 rounded-lg border border-primary/10">
                    <Film className="h-4 w-4 text-primary/60" />
                    <span className="text-sm font-medium">
                      {filledSlots.length}장 x {clipDuration}초 = <span className="text-primary">{estimatedLength}초</span>
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

              {/* 10 Slots Grid (5x2) */}
              <div>
                <h4 className="text-sm font-medium mb-3">이미지 슬롯 (최대 10장)</h4>
                <div className="grid grid-cols-5 gap-3">
                  {slots.map((slot, i) => (
                    <ImageSlot
                      key={i}
                      index={i}
                      slot={slot}
                      onFile={(f) => addFileToSlot(i, f)}
                      onRemove={() => removeSlot(i)}
                      onPromptChange={(p) => setSlotPrompt(i, p)}
                      onIncludeAudioChange={(v) => setSlotIncludeAudio(i, v)}
                    />
                  ))}
                </div>
              </div>

              {/* Error / Success */}
              {formError && <p className="text-sm text-destructive">{formError}</p>}
              {formSuccess && <p className="text-sm text-emerald-600">{formSuccess}</p>}

              {/* Submit */}
              <div className="flex items-center gap-3">
                <Button onClick={handleSubmit} disabled={submitting || filledSlots.length === 0}>
                  {submitting ? (
                    <><Loader2 className="h-4 w-4 mr-2 animate-spin" />처리 중...</>
                  ) : (
                    <><Send className="h-4 w-4 mr-2" />영상 제작 시작</>
                  )}
                </Button>
                <span className="text-xs text-muted-foreground">
                  {filledSlots.length > 0
                    ? `${filledSlots.length}장 MinIO 업로드 후 웹훅 호출`
                    : '이미지를 1장 이상 추가해주세요'}
                </span>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

// ══════════════════════════════════════════════
// Reference Image Slot (피사체/장면/스타일)
// ══════════════════════════════════════════════
function RefImageSlot({
  label,
  icon,
  preview,
  onFile,
  onRemove,
}: {
  label: string;
  icon: React.ReactNode;
  preview: string | null;
  onFile: (f: File) => void;
  onRemove: () => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);

  return (
    <div className="space-y-1.5">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      {preview ? (
        <div className="relative group aspect-square rounded-lg overflow-hidden border">
          <img src={preview} alt={label} className="w-full h-full object-cover" />
          <button
            type="button"
            onClick={onRemove}
            className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <X className="h-3 w-3" />
          </button>
        </div>
      ) : (
        <div
          onClick={() => inputRef.current?.click()}
          onDragOver={e => e.preventDefault()}
          onDrop={e => {
            e.preventDefault();
            const f = e.dataTransfer.files[0];
            if (f?.type.startsWith('image/')) onFile(f);
          }}
          className="aspect-square rounded-lg border-2 border-dashed border-muted-foreground/25 flex flex-col items-center justify-center cursor-pointer hover:border-primary/50 transition-colors"
        >
          <div className="text-muted-foreground/40">{icon}</div>
          <span className="text-xs text-muted-foreground/50 mt-1">첨부</span>
        </div>
      )}
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={e => {
          const f = e.target.files?.[0];
          if (f) onFile(f);
          e.target.value = '';
        }}
      />
    </div>
  );
}

// ══════════════════════════════════════════════
// Image Slot (10칸 그리드 개별 슬롯)
// ══════════════════════════════════════════════
function ImageSlot({
  index,
  slot,
  onFile,
  onRemove,
  onPromptChange,
  onIncludeAudioChange,
}: {
  index: number;
  slot: Slot;
  onFile: (f: File) => void;
  onRemove: () => void;
  onPromptChange: (p: string) => void;
  onIncludeAudioChange: (v: boolean) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const hasImage = !!(slot.file || slot.preview);

  return (
    <div className="space-y-1">
      {hasImage ? (
        <div className="relative group aspect-square rounded-lg overflow-hidden border">
          <img src={slot.preview!} alt={`슬롯 ${index + 1}`} className="w-full h-full object-cover" />
          <div className="absolute top-0 left-0 bg-black/50 text-white text-xs px-1.5 py-0.5 rounded-br">
            {index + 1}
          </div>
          <button
            type="button"
            onClick={onRemove}
            className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <X className="h-3 w-3" />
          </button>
          {slot.analysis && (
            <div className="absolute bottom-0 left-0 right-0 bg-black/60 text-white text-[10px] p-1.5 line-clamp-2">
              {slot.analysis}
            </div>
          )}
        </div>
      ) : (
        <div
          onClick={() => inputRef.current?.click()}
          onDragOver={e => e.preventDefault()}
          onDrop={e => {
            e.preventDefault();
            const f = e.dataTransfer.files[0];
            if (f?.type.startsWith('image/')) onFile(f);
          }}
          className="aspect-square rounded-lg border-2 border-dashed border-muted-foreground/20 flex flex-col items-center justify-center cursor-pointer hover:border-primary/40 transition-colors"
        >
          <span className="text-xs text-muted-foreground/30 font-medium">{index + 1}</span>
          <ImagePlus className="h-5 w-5 text-muted-foreground/20 mt-0.5" />
        </div>
      )}
      {hasImage && (
        <>
          <input
            type="text"
            value={slot.prompt}
            onChange={e => onPromptChange(e.target.value)}
            placeholder="개별 프롬프트"
            className="w-full text-[11px] px-1.5 py-1 rounded border border-input bg-transparent placeholder:text-muted-foreground/40 focus:outline-none focus:ring-1 focus:ring-ring"
          />
          <label className="flex items-center gap-1 cursor-pointer">
            <input
              type="checkbox"
              checked={slot.includeAudio}
              onChange={e => onIncludeAudioChange(e.target.checked)}
              className="h-3 w-3 rounded border-gray-300 accent-primary"
            />
            <span className="text-[10px] text-muted-foreground">나레이션/대사 포함</span>
          </label>
        </>
      )}
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={e => {
          const f = e.target.files?.[0];
          if (f) onFile(f);
          e.target.value = '';
        }}
      />
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
}: {
  prod: any;
  isExpanded: boolean;
  onToggle: () => void;
  videoUrl: string | null;
  thumbnailUrl: string | null;
  script: string | null;
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
        className={`border-b hover:bg-muted/50 cursor-pointer select-none transition-colors ${isExpanded ? 'bg-muted/30' : ''}`}
        onClick={onToggle}
      >
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
          <td colSpan={8} className="px-6 py-5">
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
