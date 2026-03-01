const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

/**
 * Proxy HTTP media URLs through backend to avoid mixed content blocking.
 * HTTPS URLs and relative paths are returned as-is.
 */
export function proxyMediaUrl(url: string | null | undefined): string | null {
  if (!url) return null;
  if (url.startsWith('https://') || url.startsWith('/')) return url;
  return `${API_BASE}/api/media/proxy?url=${encodeURIComponent(url)}`;
}
