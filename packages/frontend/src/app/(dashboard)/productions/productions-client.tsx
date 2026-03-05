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
} from 'lucide-react';
import Link from 'next/link';
import { proxyMediaUrl } from '@/lib/media';

const WEBHOOK_URL = 'https://n8n.srv1345711.hstgr.cloud/webhook/make-video';

export default function ProductionsClient() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [expandedId, setExpandedId] = useState<string | null>(null);

  // Quick production form
  const [showForm, setShowForm] = useState(false);
  const [promptP1, setPromptP1] = useState('');
  const [formTopic, setFormTopic] = useState('');
  const [keywords, setKeywords] = useState('');
  const [category, setCategory] = useState('');
  const [imageFiles, setImageFiles] = useState<File[]>([]);
  const [imagePreviews, setImagePreviews] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState('');
  const [formSuccess, setFormSuccess] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { data, isLoading } = useProductions({ page, status: statusFilter });
  const productions = data?.data;
  const pagination = data?.pagination;

  const addImages = useCallback((files: FileList | File[]) => {
    const newFiles = Array.from(files).filter(f => f.type.startsWith('image/'));
    const available = 4 - imageFiles.length;
    const toAdd = newFiles.slice(0, available);
    if (toAdd.length === 0) return;

    setImageFiles(prev => [...prev, ...toAdd]);
    toAdd.forEach(f => {
      const url = URL.createObjectURL(f);
      setImagePreviews(prev => [...prev, url]);
    });
  }, [imageFiles.length]);

  const removeImage = useCallback((index: number) => {
    URL.revokeObjectURL(imagePreviews[index]);
    setImageFiles(prev => prev.filter((_, i) => i !== index));
    setImagePreviews(prev => prev.filter((_, i) => i !== index));
  }, [imagePreviews]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files.length > 0) {
      addImages(e.dataTransfer.files);
    }
  }, [addImages]);

  const resetForm = () => {
    setPromptP1('');
    setFormTopic('');
    setKeywords('');
    setCategory('');
    imagePreviews.forEach(url => URL.revokeObjectURL(url));
    setImageFiles([]);
    setImagePreviews([]);
    setFormError('');
    setFormSuccess('');
  };

  const handleMakeVideo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!promptP1.trim()) {
      setFormError('프롬프트를 입력해주세요.');
      return;
    }

    setSubmitting(true);
    setFormError('');
    setFormSuccess('');

    try {
      let images: string[] | undefined;

      // Upload images to MinIO if any
      if (imageFiles.length > 0) {
        const formData = new FormData();
        imageFiles.forEach(f => formData.append('files', f));

        const token = api.getToken();
        const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
        const uploadRes = await fetch(`${API_BASE}/api/media/upload`, {
          method: 'POST',
          headers: token ? { Authorization: `Bearer ${token}` } : {},
          body: formData,
        });

        if (!uploadRes.ok) {
          const err = await uploadRes.json().catch(() => ({}));
          throw new Error(err.message || '이미지 업로드에 실패했습니다.');
        }

        const uploadData = await uploadRes.json();
        images = uploadData.data.urls;
      }

      // Build webhook payload
      const payload: Record<string, unknown> = {
        prompt_p1: promptP1.trim(),
        topic: formTopic.trim() || undefined,
        keywords: keywords.trim() || undefined,
        category: category.trim() || undefined,
      };

      if (images && images.length > 0) {
        payload.images = images;
      } else {
        payload.use_media = 'auto';
      }

      // Call n8n webhook directly
      const webhookRes = await fetch(WEBHOOK_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!webhookRes.ok) {
        throw new Error(`웹훅 호출 실패 (${webhookRes.status})`);
      }

      setFormSuccess('영상 제작이 시작되었습니다!');
      resetForm();
      setShowForm(false);
    } catch (err) {
      setFormError(err instanceof Error ? err.message : '요청에 실패했습니다.');
    } finally {
      setSubmitting(false);
    }
  };

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
                onClick={() => {
                  setStatusFilter(s.value);
                  setPage(1);
                }}
              >
                {s.label}
              </Button>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <Button onClick={() => { setShowForm(!showForm); setFormError(''); setFormSuccess(''); }}>
              {showForm ? <X className="h-4 w-4 mr-2" /> : <Send className="h-4 w-4 mr-2" />}
              {showForm ? '닫기' : '빠른 제작'}
            </Button>
            <Link href="/productions/new">
              <Button variant="outline">
                <Plus className="h-4 w-4 mr-2" />
                새 제작
              </Button>
            </Link>
          </div>
        </div>

        {/* Quick Production Form */}
        {showForm && (
          <Card>
            <CardHeader className="pb-4">
              <CardTitle className="text-lg">빠른 영상 제작</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleMakeVideo} className="space-y-4">
                {/* Prompt P1 */}
                <div className="space-y-1.5">
                  <label className="text-sm font-medium" htmlFor="prompt_p1">
                    프롬프트 <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    id="prompt_p1"
                    value={promptP1}
                    onChange={e => setPromptP1(e.target.value)}
                    placeholder="영상 제작 프롬프트를 입력하세요"
                    rows={3}
                    className="flex w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring resize-y"
                  />
                </div>

                {/* Topic / Keywords / Category */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium" htmlFor="form_topic">주제</label>
                    <Input
                      id="form_topic"
                      value={formTopic}
                      onChange={e => setFormTopic(e.target.value)}
                      placeholder="예: 역사 미스터리"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium" htmlFor="form_keywords">키워드</label>
                    <Input
                      id="form_keywords"
                      value={keywords}
                      onChange={e => setKeywords(e.target.value)}
                      placeholder="쉼표 구분"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium" htmlFor="form_category">카테고리</label>
                    <Input
                      id="form_category"
                      value={category}
                      onChange={e => setCategory(e.target.value)}
                      placeholder="예: entertainment"
                    />
                  </div>
                </div>

                {/* Image Upload */}
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">
                    사진 첨부 <span className="text-xs text-muted-foreground font-normal">(최대 4장, 없으면 자동 생성)</span>
                  </label>
                  <div
                    onDragOver={e => e.preventDefault()}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-6 text-center cursor-pointer hover:border-primary/50 transition-colors"
                  >
                    <ImagePlus className="h-8 w-8 mx-auto mb-2 text-muted-foreground/50" />
                    <p className="text-sm text-muted-foreground">
                      클릭하거나 이미지를 드래그하세요
                    </p>
                    <p className="text-xs text-muted-foreground/60 mt-1">
                      JPG, PNG, WebP, GIF (최대 10MB)
                    </p>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      multiple
                      className="hidden"
                      onChange={e => {
                        if (e.target.files) addImages(e.target.files);
                        e.target.value = '';
                      }}
                    />
                  </div>

                  {/* Image Previews */}
                  {imagePreviews.length > 0 && (
                    <div className="flex gap-3 mt-3 flex-wrap">
                      {imagePreviews.map((src, i) => (
                        <div key={i} className="relative group">
                          <img
                            src={src}
                            alt={`첨부 ${i + 1}`}
                            className="w-20 h-20 object-cover rounded-lg border"
                          />
                          <button
                            type="button"
                            onClick={() => removeImage(i)}
                            className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {formError && <p className="text-sm text-destructive">{formError}</p>}
                {formSuccess && <p className="text-sm text-emerald-600">{formSuccess}</p>}

                <div className="flex items-center gap-3">
                  <Button type="submit" disabled={submitting}>
                    {submitting ? (
                      <><Loader2 className="h-4 w-4 mr-2 animate-spin" />처리 중...</>
                    ) : (
                      <><Send className="h-4 w-4 mr-2" />영상 제작 시작</>
                    )}
                  </Button>
                  <span className="text-xs text-muted-foreground">
                    {imageFiles.length > 0
                      ? `사진 ${imageFiles.length}장 → MinIO 업로드 후 웹훅 호출`
                      : 'use_media: "auto" (kie.ai 자동 생성)'}
                  </span>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

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
                  productions?.map((prod: any) => {
                    const isExpanded = expandedId === prod.id;
                    const videoUrl = getVideoUrl(prod.assets);
                    const thumbnailUrl = getThumbnailUrl(prod.assets);
                    const script = getScript(prod.assets);

                    return (
                      <AccordionRow
                        key={prod.id}
                        prod={prod}
                        isExpanded={isExpanded}
                        onToggle={() => toggleExpand(prod.id)}
                        videoUrl={videoUrl}
                        thumbnailUrl={thumbnailUrl}
                        script={script}
                      />
                    );
                  })
                )}
              </tbody>
            </table>
          </CardContent>
        </Card>

        {/* Pagination */}
        {pagination && pagination.totalPages > 1 && (
          <div className="flex items-center justify-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm text-muted-foreground">
              {page} / {pagination.totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              disabled={page === pagination.totalPages}
              onClick={() => setPage(page + 1)}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>
    </>
  );
}

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
      await api.patch(`/api/productions/${prod.id}`, {
        status: 'failed',
        errorMessage: '사용자 중단',
      });
      queryClient.invalidateQueries({ queryKey: ['productions'] });
    } catch {
      // noop
    } finally {
      setAborting(false);
    }
  };

  const handleArchive = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('이 제작을 보관하시겠습니까?')) return;
    setArchiving(true);
    try {
      await api.patch(`/api/productions/${prod.id}`, { status: 'archived' });
      queryClient.invalidateQueries({ queryKey: ['productions'] });
    } catch {
      // noop
    } finally {
      setArchiving(false);
    }
  };

  const handleRestore = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setArchiving(true);
    try {
      await api.patch(`/api/productions/${prod.id}`, { status: 'restore' });
      queryClient.invalidateQueries({ queryKey: ['productions'] });
    } catch {
      // noop
    } finally {
      setArchiving(false);
    }
  };

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (isInProgress) {
      alert('진행중인 제작은 삭제할 수 없습니다. 먼저 중단하세요.');
      return;
    }
    if (!confirm('이 제작을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) return;
    setDeleting(true);
    try {
      await api.delete(`/api/productions/${prod.id}`);
      queryClient.invalidateQueries({ queryKey: ['productions'] });
    } catch (err: any) {
      alert(err.message || '삭제에 실패했습니다.');
    } finally {
      setDeleting(false);
    }
  };

  return (
    <>
      {/* Main row */}
      <tr
        className={`border-b hover:bg-muted/50 cursor-pointer select-none transition-colors ${
          isExpanded ? 'bg-muted/30' : ''
        }`}
        onClick={onToggle}
      >
        <td className="px-4 py-3">
          <ChevronDown
            className={`h-4 w-4 text-muted-foreground transition-transform duration-200 ${
              isExpanded ? 'rotate-180' : ''
            }`}
          />
        </td>
        <td className="px-4 py-3">
          <Badge variant="outline">{prod.channel?.name}</Badge>
        </td>
        <td className="px-4 py-3 text-muted-foreground">{prod.workflow?.name}</td>
        <td className="px-4 py-3">
          {prod.title || prod.topic ? (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-primary/5 border border-primary/10 font-medium text-sm text-foreground">
              <FileText className="h-3.5 w-3.5 text-primary/60" />
              {prod.title || prod.topic}
            </span>
          ) : (
            <span className="text-muted-foreground/50">-</span>
          )}
        </td>
        <td className="px-4 py-3">
          <div className="flex items-center gap-2">
            <StatusBadge status={prod.status} />
            {isInProgress && (
              <button
                onClick={handleAbort}
                disabled={aborting}
                className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs font-medium text-red-600 hover:bg-red-50 transition-colors"
                title="제작 중단"
              >
                <Square className="h-3 w-3" />
                {aborting ? '...' : '중단'}
              </button>
            )}
          </div>
        </td>
        <td className="px-4 py-3 text-muted-foreground text-xs">
          {prod.startedAt ? new Date(prod.startedAt).toLocaleString('ko-KR') : '-'}
        </td>
        <td className="px-4 py-3 text-muted-foreground text-xs">
          {prod.completedAt ? new Date(prod.completedAt).toLocaleString('ko-KR') : '-'}
        </td>
        <td className="px-4 py-3 text-right">
          <div className="flex items-center justify-end gap-1">
            {isArchived ? (
              <button
                onClick={handleRestore}
                disabled={archiving}
                className="p-1.5 rounded-md text-muted-foreground/50 hover:text-blue-600 hover:bg-blue-50 transition-colors"
                title="꺼내기 (복원)"
              >
                <ArchiveRestore className="h-4 w-4" />
              </button>
            ) : canArchive ? (
              <button
                onClick={handleArchive}
                disabled={archiving}
                className="p-1.5 rounded-md text-muted-foreground/50 hover:text-amber-600 hover:bg-amber-50 transition-colors"
                title="보관"
              >
                <Archive className="h-4 w-4" />
              </button>
            ) : null}
            {canDelete && (
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="p-1.5 rounded-md text-muted-foreground/50 hover:text-red-600 hover:bg-red-50 transition-colors"
                title="삭제"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            )}
          </div>
        </td>
      </tr>

      {/* Expanded detail row */}
      {isExpanded && (
        <tr className="border-b bg-muted/10">
          <td colSpan={8} className="px-6 py-5">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left: Video player or status */}
              <div className="lg:col-span-1">
                {videoUrl ? (
                  <VideoPlayer
                    src={videoUrl}
                    poster={thumbnailUrl || undefined}
                    title={prod.title || prod.topic || undefined}
                    className="max-w-[240px]"
                  />
                ) : (
                  <div className="flex items-center justify-center aspect-[9/16] max-w-[240px] mx-auto rounded-xl bg-muted/50 border border-dashed border-muted-foreground/20">
                    <div className="text-center text-muted-foreground/50">
                      <FileText className="h-8 w-8 mx-auto mb-2" />
                      <p className="text-xs">영상 없음</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Right: Details */}
              <div className="lg:col-span-2 space-y-4">
                {/* Progress stepper */}
                <div>
                  <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                    진행 상황
                  </h4>
                  <ProductionProgress status={prod.status} stepperType={prod.workflow?.stepperType || 'tts_based'} />
                </div>

                {/* Production info */}
                <div>
                  <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                    제작 정보
                  </h4>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
                    <div className="space-y-0.5">
                      <span className="text-xs text-muted-foreground">채널</span>
                      <p className="font-medium">{prod.channel?.name || '-'}</p>
                    </div>
                    <div className="space-y-0.5">
                      <span className="text-xs text-muted-foreground">워크플로우</span>
                      <p className="font-medium">{prod.workflow?.name || '-'}</p>
                    </div>
                    <div className="space-y-0.5">
                      <span className="text-xs text-muted-foreground">주제</span>
                      <p className="font-medium">{prod.topic || '-'}</p>
                    </div>
                  </div>

                  {/* Timestamps */}
                  <div className="flex flex-wrap gap-4 mt-3 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      생성: {new Date(prod.createdAt).toLocaleString('ko-KR')}
                    </div>
                    {prod.startedAt && (
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        시작: {new Date(prod.startedAt).toLocaleString('ko-KR')}
                      </div>
                    )}
                    {prod.completedAt && (
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        완료: {new Date(prod.completedAt).toLocaleString('ko-KR')}
                      </div>
                    )}
                    {prod.startedAt && prod.completedAt && (
                      <div className="flex items-center gap-1 text-emerald-600 font-medium">
                        <Clock className="h-3 w-3" />
                        소요:{' '}
                        {Math.round(
                          (new Date(prod.completedAt).getTime() -
                            new Date(prod.startedAt).getTime()) /
                            1000
                        )}
                        초
                      </div>
                    )}
                  </div>

                  {/* YouTube link */}
                  {prod.youtubeUrl && (
                    <a
                      href={prod.youtubeUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 mt-3 text-sm text-blue-600 hover:text-blue-800"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <ExternalLink className="h-3.5 w-3.5" />
                      YouTube에서 보기
                    </a>
                  )}
                </div>

                {/* Script */}
                {script && (
                  <div>
                    <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                      스크립트
                    </h4>
                    <pre className="text-xs bg-muted/60 p-3 rounded-lg overflow-auto max-h-48 whitespace-pre-wrap border">
                      {script}
                    </pre>
                  </div>
                )}

                {/* Error message */}
                {prod.errorMessage && (
                  <div>
                    {prod.errorMessage.includes('타임아웃') ? (
                      <>
                        <h4 className="text-xs font-semibold text-amber-600 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                          <Clock className="h-3.5 w-3.5" />
                          응답 시간 초과
                        </h4>
                        <pre className="text-xs bg-amber-50 text-amber-800 p-3 rounded-lg overflow-auto max-h-32 whitespace-pre-wrap border border-amber-200">
                          {prod.errorMessage}
                        </pre>
                      </>
                    ) : (
                      <>
                        <h4 className="text-xs font-semibold text-red-600 uppercase tracking-wider mb-2">
                          에러
                        </h4>
                        <pre className="text-xs bg-red-50 text-red-800 p-3 rounded-lg overflow-auto max-h-32 whitespace-pre-wrap border border-red-200">
                          {prod.errorMessage}
                        </pre>
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
