import type { Metadata } from 'next';
import { Providers } from '@/components/providers';
import { AuthGuard } from '@/components/auth-guard';
import './globals.css';

export const metadata: Metadata = {
  title: 'N8N Video Manager',
  description: '영상 자동 제작 관리 플랫폼',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-background font-sans antialiased">
        <Providers>
          <AuthGuard>
            {children}
          </AuthGuard>
        </Providers>
      </body>
    </html>
  );
}
