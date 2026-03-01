'use client';
export const runtime = 'edge';

import { Header } from '@/components/layout/header';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useChannels } from '@/hooks/use-dashboard';
import { Tv, Workflow } from 'lucide-react';
import Link from 'next/link';

export default function ChannelsPage() {
  const { data, isLoading } = useChannels();
  const channels = data?.data;

  return (
    <>
      <Header title="채널 관리" />
      <div className="p-6">
        <div className="grid gap-6 md:grid-cols-2">
          {isLoading
            ? Array.from({ length: 4 }).map((_, i) => (
                <Card key={i} className="animate-pulse">
                  <CardContent className="p-6">
                    <div className="h-32 bg-muted rounded" />
                  </CardContent>
                </Card>
              ))
            : channels?.map((channel) => (
                <Link key={channel.id} href={`/channels/${channel.id}`}>
                  <Card className="hover:shadow-md transition-shadow cursor-pointer">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
                            <Tv className="h-6 w-6 text-primary" />
                          </div>
                          <div>
                            <h3 className="text-lg font-semibold">{channel.name}</h3>
                            <p className="text-sm text-muted-foreground">{channel.slug}</p>
                          </div>
                        </div>
                        <Badge variant={channel.isActive ? 'success' : 'secondary'}>
                          {channel.isActive ? '활성' : '비활성'}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-4">
                        {channel.description}
                      </p>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Workflow className="h-4 w-4" />
                          워크플로우 {channel.workflows?.length || 0}개
                        </div>
                        <div>
                          제작 {channel._count?.productions || 0}건
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
        </div>
      </div>
    </>
  );
}
