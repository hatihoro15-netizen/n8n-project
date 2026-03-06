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

/**
 * Download a file via backend proxy to avoid CORS issues.
 */
export async function downloadViaProxy(url: string, filename: string): Promise<void> {
  const proxyUrl = `${API_BASE}/api/media/proxy?url=${encodeURIComponent(url)}`;
  const res = await fetch(proxyUrl);
  if (!res.ok) throw new Error(`Download failed: ${res.status}`);
  const blob = await res.blob();
  const blobUrl = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = blobUrl;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(blobUrl);
}
