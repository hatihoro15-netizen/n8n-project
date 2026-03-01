'use client';

import { useState } from 'react';
import { Header } from '@/components/layout/header';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
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
} from 'lucide-react';
import Link from 'next/link';

export default function ProductionsClient() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const { data, isLoading } = useProductions({ page, status: statusFilter });
  const productions = data?.data;
  const pagination = data?.pagination;

  const statuses = [
    { value: undefined, label: '전체' },
    { value: 'pending', label: '대기' },
    { value: 'triggered', label: '시작됨' },
    { value: 'completed', label: '완료' },
    { value: 'failed', label: '실패' },
  ];

  const toggleExpand = (id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  const getVideoUrl = (assets: unknown) => {
    if (!assets || typeof assets !== 'object') return null;
    const a = assets as Record<string, string>;
    return a.videoUrl || a.video_url || a.outputUrl || a.output_url || null;
  };

  const getThumbnailUrl = (assets: unknown) => {
    if (!assets || typeof assets !== 'object') return null;
    const a = assets as Record<string, string>;
    return a.thumbnailUrl || a.thumbnail_url || null;
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
          <Link href="/productions/new">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              새 제작
            </Button>
          </Link>
        </div>

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
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-muted-foreground">
                      로딩 중...
                    </td>
                  </tr>
                ) : productions?.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-muted-foreground">
                      제작 이력이 없습니다.
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
  const queryClient = useQueryClient();
  const isInProgress = !['completed', 'failed'].includes(prod.status);

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
      </tr>

      {/* Expanded detail row */}
      {isExpanded && (
        <tr className="border-b bg-muted/10">
          <td colSpan={7} className="px-6 py-5">
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
                  <ProductionProgress status={prod.status} />
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
                    <h4 className="text-xs font-semibold text-red-600 uppercase tracking-wider mb-2">
                      에러
                    </h4>
                    <pre className="text-xs bg-red-50 text-red-800 p-3 rounded-lg overflow-auto max-h-32 whitespace-pre-wrap border border-red-200">
                      {prod.errorMessage}
                    </pre>
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
