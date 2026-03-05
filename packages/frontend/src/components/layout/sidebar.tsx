'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  Play,
  Tv,
  Wand2,
  Workflow,
  Users,
  FileText,
  BarChart3,
  Image,
  Settings,
  LogOut,
} from 'lucide-react';
import { useAuthStore } from '@/stores/auth';

const navItems = [
  { href: '/', label: '대시보드', icon: LayoutDashboard },
  { href: '/productions', label: '제작 관리', icon: Play },
  { href: '/images', label: '이미지 생성', icon: Wand2 },
  { href: '/channels', label: '채널 관리', icon: Tv },
  { href: '/workflows', label: '워크플로우', icon: Workflow },
  { href: '/characters', label: '캐릭터', icon: Users },
  { href: '/prompts', label: '프롬프트', icon: FileText },
  { href: '/analytics', label: '분석', icon: BarChart3 },
  { href: '/media', label: '미디어', icon: Image },
  { href: '/settings', label: '설정', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const logout = useAuthStore((s) => s.logout);

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col border-r bg-card">
      {/* Logo */}
      <div className="flex h-16 items-center border-b px-6">
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-sm">
            N8
          </div>
          <span className="text-lg font-bold">Video Manager</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        {navItems.map((item) => {
          const isActive = pathname === item.href ||
            (item.href !== '/' && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:bg-accent hover:text-foreground'
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="border-t p-3">
        <button
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
        >
          <LogOut className="h-4 w-4" />
          로그아웃
        </button>
      </div>
    </aside>
  );
}
