export type FeedItem = {
  event: Record<string, unknown> & {
    event_id: string;
    event_tier: 'official' | 'micro';
    title: string;
  };
  score: number;
  score_breakdown: Record<string, number>;
  reasons: string[];
};

export type FeedResponse = {
  schema_version: '3.0';
  profile_id: string;
  feed_token: string;
  generated_at: string;
  candidate_count: number;
  items: FeedItem[];
  next_cursor: string | null;
  has_more: boolean;
};

export async function fetchFeed(profileId: string, cursor?: string | null, limit = 20) {
  if (!isApiConfigured()) return null;
  const params = new URLSearchParams({ profile_id: profileId, limit: String(limit) });
  if (cursor) params.set('cursor', cursor);
  return apiRequest<FeedResponse>(`/feed?${params.toString()}`, undefined, 'Etkinlik akışı alınamadı.');
}
import { apiRequest, isApiConfigured } from '@/services/api-client';
