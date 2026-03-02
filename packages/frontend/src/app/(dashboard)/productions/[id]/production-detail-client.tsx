'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { StatusBadge } from '@/components/status-badge';
import { ProductionProgress } from '@/components/production-progress';
import { VideoPlayer } from '@/components/video-player';
import { useProduction } from '@/hooks/use-dashboard';
import {
  ArrowLeft,
  ExternalLink,
  Clock,
  AlertCircle,
  RefreshCw,
  Square,
  Copy,
  Pause,
  Play,
} from 'lucide-react';
import { api } from '@/lib/api';
import { proxyMediaUrl } from '@/lib/media';
import type { StepperType } from '@n8n-web/shared';

export default function ProductionDetailClient() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const { data, isLoading, refetch } = useProduction(id);
  const production = data?.data;
  const [retrying, setRetrying] = useState(false);
  const [aborting, setAborting] = useState(false);
  const [pausing, setPausing] = useState(false);

  const isInProgress = production
    ? !['completed', 'failed', 'paused'].includes(production.status)
    : false;

  const stepperType: StepperType =
    (production?.workflow as any)?.stepperType === 'video_based'
      ? 'video_based'
      : 'tts_based';

  const handleAbort = async () => {
    if (!confirm('이 제작을 중단하시겠습니까?')) return;
    setAborting(true);
    try {
      await api.patch(`/api/productions/${id}`, {
        status: 'failed',
        errorMessage: '사용자 중단',
      });
      refetch();
    } catch {
      // noop
    } finally {
      setAborting(false);
    }
  };

  const handlePause = async () => {
    if (!confirm('제작을 정지하시겠습니까?\nn8n에서 이미 실행 중인 작업은 계속 진행되지만, 이후 콜백은 무시됩니다.')) return;
    setPausing(true);
    try {
      await api.patch(`/api/productions/${id}`, { status: 'paused' });
      refetch();
    } catch {
      // noop
    } finally {
      setPausing(false);
    }
  };

  const handleRetry = async () => {
    if (!production) return;
    if (!confirm('같은 설정으로 새 제작을 시작하시겠습니까?')) return;
    setRetrying(true);
    try {
      const res = await api.post<{ success: boolean; data: { id: string } }>('/api/productions', {
        workflowId: production.workflowId,
        topic: production.topic || undefined,
      });
      if (res.data?.id) {
        router.push(`/productions/${res.data.id}`);
      }
    } catch {
      // noop
    } finally {
      setRetrying(false);
    }
  };

  // Extract video URL from assets (proxied to avoid mixed content)
  const videoUrl = production?.assets
    ? proxyMediaUrl(
        (production.assets as Record<string, string>).videoUrl ||
        (production.assets as Record<string, string>).video_url ||
        (production.assets as Record<string, string>).outputUrl ||
        (production.assets as Record<string, string>).output_url ||
        null
      )
    : null;

  const thumbnailUrl = production?.assets
    ? proxyMediaUrl(
        (production.assets as Record<string, string>).thumbnailUrl ||
        (production.assets as Record<string, string>).thumbnail_url ||
        null
      )
    : null;

  const scriptContent = production?.assets
    ? (production.assets as Record<string, string>).script
    : null;

  if (isLoading) {
    return (
      <>
        <Header title="제작 상세" />
        <div className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-muted rounded w-48" />
            <div className="h-64 bg-muted rounded" />
          </div>
        </div>
      </>
    );
  }

  if (!production) {
    return (
      <>
        <Header title="제작 상세" />
        <div className="p-6">
          <Card>
            <CardContent className="p-12 text-center text-muted-foreground">
              <AlertCircle className="h-12 w-12 mx-auto mb-4 text-muted-foreground/30" />
              <p>제작 건을 찾을 수 없습니다.</p>
              <Link href="/productions" className="mt-4 inline-block">
                <Button variant="outline">목록으로</Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </>
    );
  }

  return (
    <>
      <Header title={production.title || production.topic || '제작 상세'} />
      <div className="p-6 space-y-6">
        {/* Back button */}
        <Link href="/productions">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            제작 목록
          </Button>
        </Link>

        {/* Progress Stepper */}
        <Card>
          <CardContent className="py-6">
            <ProductionProgress status={production.status} stepperType={stepperType} />
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Video Player or Status */}
          <div className="lg:col-span-1">
            {production.status === 'completed' && videoUrl ? (
              <div className="space-y-3">
                <VideoPlayer
                  src={videoUrl}
                  poster={thumbnailUrl || undefined}
                  title={production.title || production.topic || undefined}
                />
                <Button
                  onClick={handleRetry}
                  disabled={retrying}
                  variant="outline"
                  className="w-full"
                >
                  <Copy className="h-4 w-4 mr-2" />
                  {retrying ? '생성 중...' : '다시 만들기'}
                </Button>
              </div>
            ) : production.status === 'failed' ? (
              <Card className="border-red-200 bg-red-50/50">
                <CardContent className="p-8 text-center">
                  <AlertCircle className="h-12 w-12 mx-auto mb-4 text-red-400" />
                  <h3 className="text-lg font-medium text-red-700 mb-2">제작 실패</h3>
                  <p className="text-sm text-red-600 mb-4">
                    {production.errorMessage || '알 수 없는 오류가 발생했습니다.'}
                  </p>
                  <Button onClick={handleRetry} disabled={retrying} variant="outline">
                    <RefreshCw className={`h-4 w-4 mr-2 ${retrying ? 'animate-spin' : ''}`} />
                    {retrying ? '재시도 중...' : '같은 주제로 재시도'}
                  </Button>
                </CardContent>
              </Card>
            ) : production.status === 'paused' ? (
              <Card className="border-amber-200 bg-amber-50/50">
                <CardContent className="p-8 text-center">
                  <Pause className="h-12 w-12 mx-auto mb-4 text-amber-400" />
                  <h3 className="text-lg font-medium text-amber-700 mb-2">제작 정지됨</h3>
                  <p className="text-sm text-amber-600 mb-4">
                    이 제작은 정지된 상태입니다.
                  </p>
                  <Button onClick={handleRetry} disabled={retrying} variant="outline">
                    <Play className={`h-4 w-4 mr-2`} />
                    {retrying ? '생성 중...' : '이어서 새 제작'}
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <div className="relative mx-auto w-20 h-20 mb-4">
                    <div className="absolute inset-0 rounded-full border-4 border-muted" />
                    <div className="absolute inset-0 rounded-full border-4 border-blue-500 border-t-transparent animate-spin" />
                  </div>
                  <h3 className="text-lg font-medium mb-1">영상 제작 중...</h3>
                  <p className="text-sm text-muted-foreground">
                    <StatusBadge status={production.status} /> 단계 진행 중
                  </p>
                  <p className="text-xs text-muted-foreground mt-2">
                    자동으로 새로고침됩니다
                  </p>
                  <div className="flex items-center justify-center gap-2 mt-4">
                    <Button
                      onClick={handlePause}
                      disabled={pausing}
                      variant="outline"
                      size="sm"
                      className="text-amber-600 border-amber-200 hover:bg-amber-50"
                    >
                      <Pause className="h-3.5 w-3.5 mr-1.5" />
                      {pausing ? '정지 중...' : '정지'}
                    </Button>
                    <Button
                      onClick={handleAbort}
                      disabled={aborting}
                      variant="outline"
                      size="sm"
                      className="text-red-600 border-red-200 hover:bg-red-50"
                    >
                      <Square className="h-3.5 w-3.5 mr-1.5" />
                      {aborting ? '중단 중...' : '중단'}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right: Details */}
          <div className="lg:col-span-2 space-y-4">
            {/* Info Card */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">제작 정보</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-muted-foreground">채널</span>
                    <div className="mt-0.5">
                      <Badge variant="outline">{production.channel?.name}</Badge>
                    </div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">워크플로우</span>
                    <p className="mt-0.5 font-medium">{production.workflow?.name}</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">상태</span>
                    <div className="mt-0.5">
                      <StatusBadge status={production.status} />
                    </div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">주제</span>
                    <p className="mt-0.5 font-medium">{production.topic || '-'}</p>
                  </div>
                </div>

                {/* Timestamps */}
                <div className="border-t pt-3 space-y-2">
                  <div className="flex items-center gap-2 text-sm">
                    <Clock className="h-3.5 w-3.5 text-muted-foreground" />
                    <span className="text-muted-foreground">생성:</span>
                    <span>{new Date(production.createdAt).toLocaleString('ko-KR')}</span>
                  </div>
                  {production.startedAt && (
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="h-3.5 w-3.5 text-muted-foreground" />
                      <span className="text-muted-foreground">시작:</span>
                      <span>{new Date(production.startedAt).toLocaleString('ko-KR')}</span>
                    </div>
                  )}
                  {production.completedAt && (
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="h-3.5 w-3.5 text-muted-foreground" />
                      <span className="text-muted-foreground">완료:</span>
                      <span>{new Date(production.completedAt).toLocaleString('ko-KR')}</span>
                    </div>
                  )}
                  {production.startedAt && production.completedAt && (
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="h-3.5 w-3.5 text-emerald-500" />
                      <span className="text-muted-foreground">소요:</span>
                      <span className="font-medium text-emerald-600">
                        {Math.round(
                          (new Date(production.completedAt).getTime() -
                            new Date(production.startedAt).getTime()) /
                            1000
                        )}
                        초
                      </span>
                    </div>
                  )}
                </div>

                {/* YouTube Link */}
                {production.youtubeUrl && (
                  <div className="border-t pt-3">
                    <a
                      href={production.youtubeUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800"
                    >
                      <ExternalLink className="h-4 w-4" />
                      YouTube에서 보기
                    </a>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Script Card (if available) */}
            {scriptContent && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">스크립트</CardTitle>
                </CardHeader>
                <CardContent>
                  <pre className="text-xs bg-muted p-3 rounded-lg overflow-auto max-h-64 whitespace-pre-wrap">
                    {scriptContent}
                  </pre>
                </CardContent>
              </Card>
            )}

            {/* Error Card */}
            {production.errorMessage && (
              <Card className="border-red-200">
                <CardHeader>
                  <CardTitle className="text-base text-red-700">에러 로그</CardTitle>
                </CardHeader>
                <CardContent>
                  <pre className="text-xs bg-red-50 text-red-800 p-3 rounded-lg overflow-auto max-h-40 whitespace-pre-wrap">
                    {production.errorMessage}
                  </pre>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
