import { apiRequest, isApiConfigured } from '@/services/api-client';
import { canonicalEventId } from '@/utils/api-event';

export type InteractionAction = 'like' | 'skip' | 'save' | 'unsave' | 'view_detail' | 'apply';

export type PendingInteraction = {
  profileId: string;
  eventId: string;
  action: InteractionAction;
  dwellMs?: number;
  interactionKey: string;
  feedToken?: string;
};

export async function sendInteraction(input: PendingInteraction) {
  if (!isApiConfigured()) return null;
  return apiRequest<{ interaction_id: number; is_duplicate: boolean }>('/interactions', {
    method: 'POST',
    body: JSON.stringify({
      profile_id: input.profileId,
      event_id: canonicalEventId(input.eventId),
      action: input.action,
      dwell_ms: input.dwellMs,
      interaction_key: input.interactionKey,
      feed_token: input.feedToken,
    }),
  }, 'Etkileşim kaydedilemedi.');
}

export async function fetchSavedEvents(profileId: string) {
  if (!isApiConfigured()) return null;
  return apiRequest<{ count: number; events: Record<string, unknown>[] }>(
    `/profiles/${profileId}/saved-events`,
    undefined,
    'Kaydedilen etkinlikler alınamadı.'
  );
}
