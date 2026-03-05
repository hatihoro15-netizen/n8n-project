'use client';

import { useState, useRef } from 'react';
import { Header } from '@/components/layout/header';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useCharacters } from '@/hooks/use-dashboard';
import { useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { proxyMediaUrl } from '@/lib/media';
import { Users, Camera } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

async function uploadImageToMinIO(file: File): Promise<string> {
  const token = localStorage.getItem('token');
  const formData = new FormData();
  formData.append('files', file);
  const res = await fetch(`${API_BASE}/api/media/upload`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });
  const json = await res.json();
  if (!json.success || !json.data?.urls?.length) throw new Error('Upload failed');
  return json.data.urls[0];
}

export default function CharactersClient() {
  const { data, isLoading } = useCharacters();
  const characters = (data?.data || []) as any[];
  const queryClient = useQueryClient();

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
                <CharacterCard key={char.id} char={char} queryClient={queryClient} />
              ))}
        </div>
      </div>
    </>
  );
}

function CharacterCard({ char, queryClient }: { char: any; queryClient: any }) {
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const imgSrc = proxyMediaUrl(char.imageUrl);

  const handleImageUpload = async (file: File) => {
    setUploading(true);
    try {
      const url = await uploadImageToMinIO(file);
      await api.put(`/api/characters/${char.id}`, { imageUrl: url });
      queryClient.invalidateQueries({ queryKey: ['characters'] });
    } catch { /* noop */ } finally {
      setUploading(false);
    }
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-center gap-4 mb-4">
          <div
            className="relative group flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-primary/10 overflow-hidden cursor-pointer"
            onClick={() => fileRef.current?.click()}
          >
            {imgSrc ? (
              <img src={imgSrc} alt={char.nameKo} className="h-14 w-14 object-cover" />
            ) : (
              <Users className="h-7 w-7 text-primary" />
            )}
            <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
              {uploading ? (
                <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Camera className="h-4 w-4 text-white" />
              )}
            </div>
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={e => {
                const f = e.target.files?.[0];
                if (f) handleImageUpload(f);
                e.target.value = '';
              }}
            />
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
  );
}
