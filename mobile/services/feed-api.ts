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

const API_URL = process.env.EXPO_PUBLIC_API_URL?.replace(/\/$/, '');

export async function fetchFeed(profileId: string, cursor?: string | null, limit = 20) {
  if (!API_URL) return null;
  const params = new URLSearchParams({ profile_id: profileId, limit: String(limit) });
  if (cursor) params.set('cursor', cursor);
  const response = await fetch(`${API_URL}/feed?${params.toString()}`, {
    headers: { Accept: 'application/json' },
  });
  if (!response.ok) throw new Error(`Feed API returned ${response.status}`);
  return (await response.json()) as FeedResponse;
}
