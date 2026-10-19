import type { MessageResponse } from '../../core/api/types';

export function chronologicalMessages(pages: { items: MessageResponse[] }[] = []) {
  return [...new Map(pages.flatMap(p => p.items).map(m => [m.id, m])).values()]
    .sort((a,b) => a.created_at.localeCompare(b.created_at) || a.id.localeCompare(b.id));
}

export function submission(body: string, previous?: { body: string; nonce: string }) {
  const trimmed = body.trim();
  return previous?.body === trimmed ? previous : { body: trimmed, nonce: crypto.randomUUID() };
}

export function isUnavailable(error: unknown) {
  return [403,404].includes((error as { statusCode?: number })?.statusCode || 0);
}
