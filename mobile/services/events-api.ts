import { apiRequest, isApiConfigured } from '@/services/api-client';
import { canonicalEventId } from '@/utils/api-event';

export type MicroEventPayload = {
  creatorProfileId: string;
  title: string;
  description: string;
  categoryId: string;
  interestIds: string[];
  targetGoalIds: string[];
  startsAt: string;
  endsAt: string;
  expiresAt: string;
  participationMode: 'onsite' | 'online' | 'hybrid';
  locationName: string;
  quota: number;
  language: 'tr' | 'en' | 'mixed';
};

export async function createMicroEvent(input: MicroEventPayload) {
  return apiRequest<Record<string, unknown>>('/events', {
    method: 'POST',
    body: JSON.stringify({
      creator_profile_id: input.creatorProfileId,
      title: input.title,
      description: input.description,
      category_id: input.categoryId,
      interest_ids: input.interestIds,
      target_goal_ids: input.targetGoalIds,
      starts_at: input.startsAt,
      ends_at: input.endsAt,
      expires_at: input.expiresAt,
      participation_mode: input.participationMode,
      location_name: input.locationName,
      quota: input.quota,
      language: input.language,
    }),
  }, 'Mikro etkinlik oluşturulamadı.');
}

export async function applyToEvent(eventId: string, profileId: string) {
  return apiRequest<{ participation_id: string; status: string; is_duplicate: boolean }>(
    `/events/${canonicalEventId(eventId)}/apply`,
    {
    method: 'POST',
    body: JSON.stringify({ profile_id: profileId }),
    },
    'Katılım isteği oluşturulamadı.'
  );
}

export type Participation = {
  participation_id: string;
  event_id: string;
  title: string;
  starts_at: string;
  location_name: string | null;
  status: 'requested' | 'approved' | 'rejected' | 'cancelled' | 'attended' | 'no_show';
  attendance_verified: number;
  has_rated: number;
  requested_at: string;
};

export async function fetchParticipations(profileId: string) {
  if (!isApiConfigured()) return null;
  return apiRequest<{ count: number; participations: Participation[] }>(
    `/profiles/${profileId}/participations`,
    undefined,
    'Katılım geçmişi alınamadı.'
  );
}

export async function rateEvent(eventId: string, profileId: string, score: number) {
  return apiRequest<{ rating_id: string; score: number; is_anonymous: boolean }>(
    `/events/${canonicalEventId(eventId)}/ratings`,
    {
      method: 'POST',
      body: JSON.stringify({ profile_id: profileId, score }),
    },
    'Puan kaydedilemedi.'
  );
}
