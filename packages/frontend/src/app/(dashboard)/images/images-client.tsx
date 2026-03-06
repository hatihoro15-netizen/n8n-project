'use client';

import { useState, useRef } from 'react';
import { Header } from '@/components/layout/header';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import {
  Upload,
  X,
  Loader2,
  Wand2,
  Eye,
  EyeOff,
  Download,
  RefreshCw,
  Film,
  ChevronDown,
  ChevronUp,
  Plus,
} from 'lucide-react';
import { useRouter } from 'next/navigation';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

// ── Types ──
type SlotData = {
  file: File | null;
  preview: string | null;
  url: string | null;
  analysis: string | null;
  analyzing: boolean;
  use: boolean;
};

type GeneratedImage = {
  url: string;
  saving: boolean;
  saved: boolean;
  selected: boolean;
};

type MyPhoto = {
  id: string;
  file: File | null;
  preview: string | null;
  url: string | null;
  analysis: string | null;
  analyzing: boolean;
  useMode: 'direct' | 'generate' | 'analysis_only';
  autoPrompt: string | null;
};

function emptyMyPhoto(): MyPhoto {
  return {
    id: Math.random().toString(36).slice(2),
    file: null, preview: null, url: null,
    analysis: null, analyzing: false,
    useMode: 'direct', autoPrompt: null,
  };
}

function emptySlot(): SlotData {
  return { file: null, preview: null, url: null, analysis: null, analyzing: false, use: true };
}

// ── Helper: upload to MinIO ──
async function uploadToMinIO(file: File): Promise<string> {
  const formData = new FormData();
  formData.append('files', file);
  const token = api.getToken();
  const res = await fetch(`${API_BASE}/api/media/upload`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });
  if (!res.ok) throw new Error('Upload failed');
  const data = await res.json();
  return data.data.urls[0];
}

// ── Helper: analyze image via Claude Vision ──
async function analyzeImage(imageUrl: string): Promise<string> {
  const token = api.getToken();
  const res = await fetch(`${API_BASE}/api/media/analyze-image`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ imageUrl }),
  });
  if (!res.ok) return '';
  const data = await res.json();
  return data.data?.analysis || '';
}

// ══════════════════════════════════════════════
// Main Component
// ══════════════════════════════════════════════
export default function ImagesClient() {
  const router = useRouter();

  // Aspect ratio
  const [aspectRatio, setAspectRatio] = useState<'9:16' | '16:9'>('9:16');

  // 3 Whisk slots
  const [subject, setSubject] = useState<SlotData>(emptySlot());
  const [scene, setScene] = useState<SlotData>(emptySlot());
  const [style, setStyle] = useState<SlotData>(emptySlot());

  // My Photos
  const [myPhotos, setMyPhotos] = useState<MyPhoto[]>([emptyMyPhoto()]);
  const [showMyPhotos, setShowMyPhotos] = useState(false);

  // Prompt + count
  const [prompt, setPrompt] = useState('');
  const [count, setCount] = useState<1 | 2 | 3>(1);

  // Generation
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState<GeneratedImage[]>([]);

  // Slot upload handler
  const handleSlotUpload = async (
    file: File,
    setter: React.Dispatch<React.SetStateAction<SlotData>>,
  ) => {
    if (!file.type.startsWith('image/')) return;
    const preview = URL.createObjectURL(file);
    setter(prev => ({ ...prev, file, preview, url: null, analysis: null, analyzing: true }));

    try {
      const url = await uploadToMinIO(file);
      setter(prev => ({ ...prev, url }));
      const analysis = await analyzeImage(url);
      setter(prev => ({ ...prev, analysis, analyzing: false }));
    } catch {
      setter(prev => ({ ...prev, analyzing: false }));
    }
  };

  const clearSlot = (setter: React.Dispatch<React.SetStateAction<SlotData>>, current: SlotData) => {
    if (current.preview) URL.revokeObjectURL(current.preview);
    setter(emptySlot());
  };

  // My photo handlers
  const handleMyPhotoUpload = async (id: string, file: File) => {
    if (!file.type.startsWith('image/')) return;
    const preview = URL.createObjectURL(file);
    setMyPhotos(prev => prev.map(p =>
      p.id === id ? { ...p, file, preview, url: null, analysis: null, analyzing: true } : p
    ));
    try {
      const url = await uploadToMinIO(file);
      setMyPhotos(prev => prev.map(p => p.id === id ? { ...p, url } : p));
      const analysis = await analyzeImage(url);
      setMyPhotos(prev => prev.map(p =>
        p.id === id ? { ...p, analysis, analyzing: false, autoPrompt: analysis } : p
      ));
    } catch {
      setMyPhotos(prev => prev.map(p => p.id === id ? { ...p, analyzing: false } : p));
    }
  };

  // Active slot count
  const activeSlots = [subject, scene, style].filter(s => s.url && s.use);
  const canGenerate = prompt.trim().length > 0 && !generating;

  // Generate images
  const handleGenerate = async () => {
    if (!canGenerate) return;
    setGenerating(true);
    setError('');

    try {
      const token = api.getToken();
      const body: Record<string, unknown> = {
        prompt: prompt.trim(),
        count,
        aspect_ratio: aspectRatio,
      };
      if (subject.url && subject.use) body.ref_subject = subject.url;
      if (scene.url && scene.use) body.ref_scene = scene.url;
      if (style.url && style.use) body.ref_style = style.url;

      const myImagesPayload = myPhotos
        .filter(p => p.url)
        .map(p => ({
          url: p.url!,
          use_mode: p.useMode,
          analysis: p.analysis || '',
          auto_prompt: p.autoPrompt || '',
        }));
      if (myImagesPayload.length > 0) body.my_images = myImagesPayload;

      const res = await fetch(`${API_BASE}/api/media/generate-image`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(body),
      });

      const data = await res.json();
      if (data.data?.images?.length) {
        setResults(data.data.images.map((url: string) => ({ url, saving: false, saved: false, selected: true })));
      } else {
        setError('이미지 생성에 실패했습니다. 다시 시도해주세요.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '이미지 생성 실패');
    } finally {
      setGenerating(false);
    }
  };

  // Save generated image to MinIO (download from kie.ai → re-upload)
  const handleSave = async (index: number) => {
    setResults(prev => prev.map((r, i) => i === index ? { ...r, saving: true } : r));
    try {
      const token = api.getToken();
      // Use backend proxy to fetch external image and store
      const res = await fetch(`${API_BASE}/api/media/save-external`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ url: results[index].url }),
      });
      if (res.ok) {
        const data = await res.json();
        setResults(prev => prev.map((r, i) =>
          i === index ? { ...r, url: data.data?.url || r.url, saving: false, saved: true } : r
        ));
      } else {
        setResults(prev => prev.map((r, i) => i === index ? { ...r, saving: false } : r));
      }
    } catch {
      setResults(prev => prev.map((r, i) => i === index ? { ...r, saving: false } : r));
    }
  };

  // Send selected images to productions page
  const handleSendToProductions = () => {
    const selectedUrls = results.filter(r => r.selected).map(r => r.url);
    if (selectedUrls.length === 0) return;
    try {
      const existing = JSON.parse(localStorage.getItem('pending_production_images') || '[]');
      localStorage.setItem('pending_production_images', JSON.stringify([...existing, ...selectedUrls]));
    } catch {
      localStorage.setItem('pending_production_images', JSON.stringify(selectedUrls));
    }
    router.push('/productions');
  };

  // Download image
  const handleDownload = async (url: string, index: number) => {
    try {
      const res = await fetch(url);
      const blob = await res.blob();
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `generated-image-${index + 1}.${blob.type.includes('png') ? 'png' : 'jpg'}`;
      a.click();
      URL.revokeObjectURL(a.href);
    } catch { /* ignore */ }
  };

  return (
    <>
      <Header title="이미지 생성" />
      <div className="p-6 space-y-6">
        <Card>
          <CardContent className="p-6 space-y-5">
            {/* 1. Aspect Ratio */}
            <div>
              <h4 className="text-sm font-medium mb-2">영상 비율</h4>
              <div className="grid grid-cols-2 gap-3 max-w-md">
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

            {/* 2. Three Whisk Slots */}
            <div>
              <h4 className="text-sm font-medium mb-3">참조 이미지 (Whisk)</h4>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <WhiskSlot
                  label="피사체 (Subject)"
                  description="주인공/인물/오브젝트"
                  slot={subject}
                  onUpload={(f) => handleSlotUpload(f, setSubject)}
                  onClear={() => clearSlot(setSubject, subject)}
                  onToggleUse={() => setSubject(prev => ({ ...prev, use: !prev.use }))}
                />
                <WhiskSlot
                  label="장면 (Scene)"
                  description="배경/상황/장소"
                  slot={scene}
                  onUpload={(f) => handleSlotUpload(f, setScene)}
                  onClear={() => clearSlot(setScene, scene)}
                  onToggleUse={() => setScene(prev => ({ ...prev, use: !prev.use }))}
                />
                <WhiskSlot
                  label="스타일 (Style)"
                  description="분위기/화풍/톤"
                  slot={style}
                  onUpload={(f) => handleSlotUpload(f, setStyle)}
                  onClear={() => clearSlot(setStyle, style)}
                  onToggleUse={() => setStyle(prev => ({ ...prev, use: !prev.use }))}
                />
              </div>
            </div>

            {/* 2.5 내 사진으로 만들기 */}
            <div>
              <button
                type="button"
                onClick={() => setShowMyPhotos(!showMyPhotos)}
                className="flex items-center gap-2 text-sm font-medium w-full text-left"
              >
                {showMyPhotos ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                내 사진으로 만들기
                <span className="text-xs text-muted-foreground font-normal">(선택사항)</span>
              </button>

              {showMyPhotos && (
                <div className="mt-3 space-y-3">
                  <p className="text-xs text-muted-foreground">
                    내 사진을 업로드하면 AI가 분석하여 이미지 생성에 반영합니다.
                  </p>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
                    {myPhotos.map(photo => (
                      <MyPhotoCard
                        key={photo.id}
                        photo={photo}
                        onUpload={(file) => handleMyPhotoUpload(photo.id, file)}
                        onRemove={() => {
                          if (photo.preview) URL.revokeObjectURL(photo.preview);
                          setMyPhotos(prev =>
                            prev.length <= 1 ? [emptyMyPhoto()] : prev.filter(p => p.id !== photo.id)
                          );
                        }}
                        onUpdate={(updates) =>
                          setMyPhotos(prev => prev.map(p =>
                            p.id === photo.id ? { ...p, ...updates } : p
                          ))
                        }
                      />
                    ))}
                  </div>
                  {myPhotos.length < 10 && (
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => setMyPhotos(prev => [...prev, emptyMyPhoto()])}
                    >
                      <Plus className="h-3.5 w-3.5 mr-1" />
                      추가
                    </Button>
                  )}
                </div>
              )}
            </div>

            {/* 3. Prompt */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium" htmlFor="gen_prompt">
                프롬프트 <span className="text-red-500">*</span>
              </label>
              <textarea
                id="gen_prompt"
                value={prompt}
                onChange={e => setPrompt(e.target.value)}
                placeholder="예: 총쏘는 사람, 웃으면서 우는 사람"
                rows={3}
                className="flex w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring resize-y"
              />
            </div>

            {/* 4. Count */}
            <div>
              <h4 className="text-sm font-medium mb-2">생성 개수</h4>
              <div className="flex gap-2">
                {([1, 2, 3] as const).map(n => (
                  <Button
                    key={n}
                    type="button"
                    variant={count === n ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setCount(n)}
                  >
                    {n}개
                  </Button>
                ))}
              </div>
            </div>

            {/* Error */}
            {error && <p className="text-sm text-destructive">{error}</p>}

            {/* 5. Generate Button */}
            <Button onClick={handleGenerate} disabled={!canGenerate} className="w-full sm:w-auto">
              {generating ? (
                <><Loader2 className="h-4 w-4 mr-2 animate-spin" />생성 중...</>
              ) : (
                <><Wand2 className="h-4 w-4 mr-2" />이미지 생성</>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* 6. Results Grid */}
        {results.length > 0 && (
          <Card>
            <CardContent className="p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-medium">생성 결과</h4>
                <span className="text-xs text-muted-foreground">
                  {results.filter(r => r.selected).length}/{results.length}개 선택
                </span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {results.map((img, i) => (
                  <div key={i} className={`border rounded-lg overflow-hidden bg-white transition-colors ${img.selected ? 'border-primary ring-1 ring-primary/30' : ''}`}>
                    <div className={`relative bg-muted/30 ${aspectRatio === '9:16' ? 'aspect-[9/16]' : 'aspect-video'}`}>
                      <img
                        src={img.url}
                        alt={`생성 이미지 ${i + 1}`}
                        className="w-full h-full object-cover"
                      />
                      {/* Checkbox overlay */}
                      <label className="absolute top-2 left-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={img.selected}
                          onChange={() => setResults(prev => prev.map((r, j) =>
                            j === i ? { ...r, selected: !r.selected } : r
                          ))}
                          className="h-4 w-4 rounded border-gray-300 accent-primary"
                        />
                      </label>
                    </div>
                    <div className="flex items-center gap-2 p-3">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleSave(i)}
                        disabled={img.saving || img.saved}
                      >
                        {img.saving ? (
                          <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" />
                        ) : (
                          <Download className="h-3.5 w-3.5 mr-1" />
                        )}
                        {img.saved ? '저장됨' : '저장'}
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDownload(img.url, i)}
                      >
                        <Download className="h-3.5 w-3.5 mr-1" />
                        다운로드
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
              <div className="flex items-center gap-2 pt-2">
                <Button
                  type="button"
                  onClick={handleSendToProductions}
                  disabled={results.filter(r => r.selected).length === 0}
                >
                  <Film className="h-3.5 w-3.5 mr-1" />
                  선택한 이미지로 영상 제작 ({results.filter(r => r.selected).length}개)
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleGenerate}
                  disabled={generating}
                >
                  <RefreshCw className={`h-3.5 w-3.5 mr-1 ${generating ? 'animate-spin' : ''}`} />
                  재생성
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </>
  );
}

// ══════════════════════════════════════════════
// Whisk Slot Component
// ══════════════════════════════════════════════
function WhiskSlot({
  label,
  description,
  slot,
  onUpload,
  onClear,
  onToggleUse,
}: {
  label: string;
  description: string;
  slot: SlotData;
  onUpload: (file: File) => void;
  onClear: () => void;
  onToggleUse: () => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium">{label}</p>
          <p className="text-xs text-muted-foreground">{description}</p>
        </div>
        {slot.preview && (
          <button
            type="button"
            onClick={onToggleUse}
            className={`flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium transition-colors ${
              slot.use
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                : 'bg-gray-50 text-gray-500 border border-gray-200'
            }`}
          >
            {slot.use ? <><Eye className="h-3 w-3" />유</> : <><EyeOff className="h-3 w-3" />무</>}
          </button>
        )}
      </div>

      {!slot.preview ? (
        <>
          <div
            onDragOver={e => e.preventDefault()}
            onDrop={e => { e.preventDefault(); if (e.dataTransfer.files[0]) onUpload(e.dataTransfer.files[0]); }}
            onClick={() => inputRef.current?.click()}
            className="border-2 border-dashed border-muted-foreground/20 rounded-lg flex flex-col items-center justify-center min-h-[160px] cursor-pointer hover:border-primary/40 transition-colors"
          >
            <Upload className="h-6 w-6 text-muted-foreground/40 mb-2" />
            <p className="text-xs text-muted-foreground">드래그 또는 클릭</p>
          </div>
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={e => {
              if (e.target.files?.[0]) onUpload(e.target.files[0]);
              e.target.value = '';
            }}
          />
        </>
      ) : (
        <div className={`relative border rounded-lg overflow-hidden group ${!slot.use ? 'opacity-40' : ''}`}>
          <div className="relative aspect-square bg-muted/30">
            <img src={slot.preview} alt={label} className="w-full h-full object-cover" />
            <button
              type="button"
              onClick={onClear}
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
          {slot.analysis && (
            <div className="p-2 text-xs text-muted-foreground line-clamp-3 bg-muted/30">
              {slot.analysis}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ══════════════════════════════════════════════
// My Photo Card Component
// ══════════════════════════════════════════════
function MyPhotoCard({
  photo,
  onUpload,
  onRemove,
  onUpdate,
}: {
  photo: MyPhoto;
  onUpload: (file: File) => void;
  onRemove: () => void;
  onUpdate: (updates: Partial<MyPhoto>) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);

  return (
    <div className="border rounded-lg overflow-hidden relative group">
      <button
        type="button"
        onClick={onRemove}
        className="absolute top-1 right-1 z-10 bg-red-500 text-white rounded-full p-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
      >
        <X className="h-3 w-3" />
      </button>

      {!photo.preview ? (
        <>
          <div
            onDragOver={e => e.preventDefault()}
            onDrop={e => { e.preventDefault(); if (e.dataTransfer.files[0]) onUpload(e.dataTransfer.files[0]); }}
            onClick={() => inputRef.current?.click()}
            className="border-2 border-dashed border-muted-foreground/20 rounded-lg flex flex-col items-center justify-center h-32 cursor-pointer hover:border-primary/40 transition-colors m-2"
          >
            <Upload className="h-5 w-5 text-muted-foreground/40 mb-1" />
            <p className="text-xs text-muted-foreground">이미지 업로드</p>
          </div>
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={e => { if (e.target.files?.[0]) onUpload(e.target.files[0]); e.target.value = ''; }}
          />
        </>
      ) : (
        <div className="space-y-2">
          <div className="relative aspect-square bg-muted/30">
            <img src={photo.preview} alt="내 사진" className="w-full h-full object-cover" />
            {photo.analyzing && (
              <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
                <Loader2 className="h-5 w-5 text-white animate-spin" />
              </div>
            )}
          </div>
          {photo.analysis && (
            <p className="px-2 text-xs text-muted-foreground line-clamp-2">{photo.analysis}</p>
          )}

          <div className="px-2 pb-2 space-y-1">
            {(['direct', 'generate', 'analysis_only'] as const).map(mode => (
              <label key={mode} className="flex items-center gap-1.5 text-xs cursor-pointer">
                <input
                  type="radio"
                  name={`photo-mode-${photo.id}`}
                  checked={photo.useMode === mode}
                  onChange={() => onUpdate({ useMode: mode })}
                  className="h-3 w-3"
                />
                {mode === 'direct' && '직접 사용'}
                {mode === 'generate' && '새 이미지 생성'}
                {mode === 'analysis_only' && '분석만 반영'}
              </label>
            ))}
            {photo.useMode === 'analysis_only' && (
              <textarea
                value={photo.autoPrompt || ''}
                onChange={e => onUpdate({ autoPrompt: e.target.value })}
                placeholder="자동 생성된 프롬프트 (수정 가능)"
                rows={2}
                className="w-full mt-1 rounded-md border border-input bg-transparent px-2 py-1 text-xs shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring resize-y"
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
