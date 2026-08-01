export type InteractionAction = 'like' | 'skip' | 'save' | 'unsave' | 'view_detail' | 'apply';

export type PendingInteraction = {
  profileId: string;
  eventId: string;
  action: InteractionAction;
  dwellMs?: number;
  interactionKey: string;
  feedToken?: string;
};

const API_URL = process.env.EXPO_PUBLIC_API_URL?.replace(/\/$/, '');

export async function sendInteraction(input: PendingInteraction) {
  if (!API_URL) return null;
  const response = await fetch(`${API_URL}/interactions`, {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify({
      profile_id: input.profileId,
      event_id: input.eventId,
      action: input.action,
      dwell_ms: input.dwellMs,
      interaction_key: input.interactionKey,
      feed_token: input.feedToken,
    }),
  });
  if (!response.ok) throw new Error(`Interaction API returned ${response.status}`);
  return response.json() as Promise<{ interaction_id: number; is_duplicate: boolean }>;
}

export async function fetchSavedEvents(profileId: string) {
  if (!API_URL) return null;
  const response = await fetch(`${API_URL}/profiles/${profileId}/saved-events`, {
    headers: { Accept: 'application/json' },
  });
  if (!response.ok) throw new Error(`Saved events API returned ${response.status}`);
  return (await response.json()) as { count: number; events: Record<string, unknown>[] };
}
