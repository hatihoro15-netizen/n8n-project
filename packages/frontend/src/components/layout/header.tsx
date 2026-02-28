'use client';

import { useAuthStore } from '@/stores/auth';

export function Header({ title }: { title?: string }) {
  const user = useAuthStore((s) => s.user);

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b bg-background/95 backdrop-blur px-6">
      <h1 className="text-xl font-semibold">{title || ''}</h1>
      <div className="flex items-center gap-4">
        <span className="text-sm text-muted-foreground">
          {user?.username}
        </span>
      </div>
    </header>
  );
}
