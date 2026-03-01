'use client';

import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { StatusBadge } from '@/components/status-badge';
import { useDashboardStats } from '@/hooks/use-dashboard';
import { Play, CheckCircle, XCircle, Clock, Tv, Plus } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';

export default function DashboardPage() {
  const router = useRouter();
  const { data, isLoading } = useDashboardStats();
  const stats = data?.data;

  return (
    <>
      <Header title="대시보드" />
      <div className="p-6 space-y-6">
        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatCard
            title="전체 제작"
            value={stats?.totalProductions ?? '-'}
            icon={<Play className="h-4 w-4" />}
            loading={isLoading}
          />
          <StatCard
            title="오늘 완료"
            value={stats?.completedToday ?? '-'}
            icon={<CheckCircle className="h-4 w-4 text-green-600" />}
            loading={isLoading}
          />
          <StatCard
            title="오늘 실패"
            value={stats?.failedToday ?? '-'}
            icon={<XCircle className="h-4 w-4 text-red-600" />}
            loading={isLoading}
          />
          <StatCard
            title="진행 중"
            value={stats?.activeProductions ?? '-'}
            icon={<Clock className="h-4 w-4 text-yellow-600" />}
            loading={isLoading}
          />
        </div>

        {/* Quick Create */}
        <div className="flex justify-end">
          <Link href="/productions/new">
            <Button size="lg" className="gap-2">
              <Plus className="h-5 w-5" />
              영상 제작하기
            </Button>
          </Link>
        </div>

        {/* Channel Cards */}
        <div>
          <h2 className="text-lg font-semibold mb-4">채널 현황</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {isLoading
              ? Array.from({ length: 4 }).map((_, i) => (
                  <Card key={i} className="animate-pulse">
                    <CardContent className="p-6">
                      <div className="h-16 bg-muted rounded" />
                    </CardContent>
                  </Card>
                ))
              : stats?.channelStats?.map((ch) => (
                  <Link key={ch.channelId} href={`/channels/${ch.channelId}`}>
                    <Card className="hover:shadow-md transition-shadow cursor-pointer">
                      <CardContent className="p-6">
                        <div className="flex items-center gap-3 mb-3">
                          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                            <Tv className="h-5 w-5 text-primary" />
                          </div>
                          <div>
                            <h3 className="font-semibold">{ch.channelName}</h3>
                            <p className="text-xs text-muted-foreground">
                              {ch.totalProductions}건 제작
                            </p>
                          </div>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          최근:{' '}
                          {ch.lastProductionAt
                            ? new Date(ch.lastProductionAt).toLocaleDateString('ko-KR')
                            : '아직 없음'}
                        </p>
                      </CardContent>
                    </Card>
                  </Link>
                ))}
          </div>
        </div>

        {/* Recent Productions */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">최근 제작</h2>
            <Link href="/productions" className="text-sm text-primary hover:underline">
              전체 보기
            </Link>
          </div>
          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="px-4 py-3 text-left font-medium">채널</th>
                      <th className="px-4 py-3 text-left font-medium">워크플로우</th>
                      <th className="px-4 py-3 text-left font-medium">제목</th>
                      <th className="px-4 py-3 text-left font-medium">상태</th>
                      <th className="px-4 py-3 text-left font-medium">일시</th>
                    </tr>
                  </thead>
                  <tbody>
                    {isLoading ? (
                      <tr>
                        <td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">
                          로딩 중...
                        </td>
                      </tr>
                    ) : stats?.recentProductions?.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">
                          아직 제작 이력이 없습니다.
                        </td>
                      </tr>
                    ) : (
                      stats?.recentProductions?.map((prod: any) => (
                        <tr
                          key={prod.id}
                          className="border-b hover:bg-muted/50 cursor-pointer"
                          onClick={() => router.push(`/productions/${prod.id}`)}
                        >
                          <td className="px-4 py-3">
                            <Badge variant="outline">{prod.channel?.name}</Badge>
                          </td>
                          <td className="px-4 py-3 text-muted-foreground">
                            {prod.workflow?.name}
                          </td>
                          <td className="px-4 py-3">
                            {prod.title || prod.topic || '-'}
                          </td>
                          <td className="px-4 py-3">
                            <StatusBadge status={prod.status} />
                          </td>
                          <td className="px-4 py-3 text-muted-foreground">
                            {new Date(prod.createdAt).toLocaleString('ko-KR')}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
}

function StatCard({
  title,
  value,
  icon,
  loading,
}: {
  title: string;
  value: number | string;
  icon: React.ReactNode;
  loading: boolean;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="h-8 w-16 animate-pulse bg-muted rounded" />
        ) : (
          <div className="text-2xl font-bold">{value}</div>
        )}
      </CardContent>
    </Card>
  );
}
