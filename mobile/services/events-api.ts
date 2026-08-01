const API_URL = process.env.EXPO_PUBLIC_API_URL?.replace(/\/$/, '');

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
  if (!API_URL) throw new Error('Mobil API adresi tanımlı değil.');
  const response = await fetch(`${API_URL}/events`, {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
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
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload?.error?.message ?? 'Mikro etkinlik oluşturulamadı.');
  }
  return payload as Record<string, unknown>;
}

export async function applyToEvent(eventId: string, profileId: string) {
  if (!API_URL) throw new Error('Mobil API adresi tanımlı değil.');
  const response = await fetch(`${API_URL}/events/${eventId}/apply`, {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile_id: profileId }),
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload?.error?.message ?? 'Katılım isteği oluşturulamadı.');
  }
  return payload as { participation_id: string; status: string; is_duplicate: boolean };
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
  if (!API_URL) return null;
  const response = await fetch(`${API_URL}/profiles/${profileId}/participations`, {
    headers: { Accept: 'application/json' },
  });
  if (!response.ok) throw new Error('Katılım geçmişi alınamadı.');
  return (await response.json()) as { count: number; participations: Participation[] };
}

export async function rateEvent(eventId: string, profileId: string, score: number) {
  if (!API_URL) throw new Error('Mobil API adresi tanımlı değil.');
  const response = await fetch(`${API_URL}/events/${eventId}/ratings`, {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile_id: profileId, score }),
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload?.error?.message ?? 'Puan kaydedilemedi.');
  return payload as { rating_id: string; score: number; is_anonymous: boolean };
}
