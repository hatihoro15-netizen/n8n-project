'use client';

import { Header } from '@/components/layout/header';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useCharacters } from '@/hooks/use-dashboard';
import { Users } from 'lucide-react';

export default function CharactersClient() {
  const { data, isLoading } = useCharacters();
  const characters = (data?.data || []) as any[];

  return (
    <>
      <Header title="캐릭터" />
      <div className="p-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {isLoading
            ? Array.from({ length: 3 }).map((_, i) => (
                <Card key={i} className="animate-pulse">
                  <CardContent className="p-6">
                    <div className="h-40 bg-muted rounded" />
                  </CardContent>
                </Card>
              ))
            : characters.map((char) => (
                <Card key={char.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-4 mb-4">
                      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/10">
                        <Users className="h-7 w-7 text-primary" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold">{char.nameKo}</h3>
                        <p className="text-sm text-muted-foreground">{char.name}</p>
                      </div>
                      <div className="ml-auto">
                        <Badge variant={char.isActive ? 'success' : 'secondary'}>
                          {char.isActive ? '활성' : '비활성'}
                        </Badge>
                      </div>
                    </div>
                    {char.personality && (
                      <div className="mb-3">
                        <p className="text-xs font-medium text-muted-foreground mb-1">성격</p>
                        <p className="text-sm">{char.personality}</p>
                      </div>
                    )}
                    {char.speechStyle && (
                      <div className="mb-3">
                        <p className="text-xs font-medium text-muted-foreground mb-1">말투</p>
                        <p className="text-sm">{char.speechStyle}</p>
                      </div>
                    )}
                    {char.workflows?.length > 0 && (
                      <div className="flex gap-1 mt-3 pt-3 border-t">
                        {char.workflows.map((wc: any) => (
                          <Badge key={wc.workflowId} variant="outline" className="text-xs">
                            {wc.workflow?.name}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
        </div>
      </div>
    </>
  );
}
