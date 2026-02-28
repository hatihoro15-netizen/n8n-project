'use client';

import { useState } from 'react';
import { Header } from '@/components/layout/header';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { StatusBadge } from '@/components/status-badge';
import { useProductions } from '@/hooks/use-dashboard';
import { Plus, ChevronLeft, ChevronRight } from 'lucide-react';
import Link from 'next/link';

export default function ProductionsPage() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string | undefined>();

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
                    <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
                      로딩 중...
                    </td>
                  </tr>
                ) : productions?.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
                      제작 이력이 없습니다.
                    </td>
                  </tr>
                ) : (
                  productions?.map((prod: any) => (
                    <tr key={prod.id} className="border-b hover:bg-muted/50">
                      <td className="px-4 py-3">
                        <Badge variant="outline">{prod.channel?.name}</Badge>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">{prod.workflow?.name}</td>
                      <td className="px-4 py-3">{prod.title || prod.topic || '-'}</td>
                      <td className="px-4 py-3">
                        <StatusBadge status={prod.status} />
                      </td>
                      <td className="px-4 py-3 text-muted-foreground text-xs">
                        {prod.startedAt ? new Date(prod.startedAt).toLocaleString('ko-KR') : '-'}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground text-xs">
                        {prod.completedAt ? new Date(prod.completedAt).toLocaleString('ko-KR') : '-'}
                      </td>
                    </tr>
                  ))
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
