import type { StudentProfile } from '@/context/app-context';
import { events as fallbackEvents } from '@/mocks/events';
import type { CampusEvent } from '@/types/event';

export type InteractionAction = 'like' | 'skip' | 'save' | 'unsave' | 'view_detail';

const API_URL = process.env.EXPO_PUBLIC_API_URL?.replace(/\/$/, '');
const REQUEST_TIMEOUT_MS = 5000;

export function isApiConfigured() {
  return Boolean(API_URL);
}

export function toProfileRequest(profile: StudentProfile) {
  return {
    schema_version: profile.schemaVersion,
    education_reference_version: profile.educationReferenceVersion,
    display_name: profile.displayName,
    university_id: profile.universityId,
    university_name: profile.universityName,
    program_id: profile.programId,
    program_name: profile.programName,
    education_level: profile.educationLevel,
    program_duration: profile.programDuration,
    class_year: profile.classYear,
    interest_ids: profile.interestIds,
    participation_goal_ids: profile.participationGoalIds,
    participation_modes: profile.participationModes,
    fee_preference: profile.feePreference,
    language_preference: profile.languagePreference,
    campus_id: profile.campusId,
  };
}

async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  if (!API_URL) throw new Error('EXPO_PUBLIC_API_URL tanımlı değil.');

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: {
        Accept: 'application/json',
        ...(init?.body ? { 'Content-Type': 'application/json' } : {}),
        ...init?.headers,
      },
      signal: controller.signal,
    });
    if (!response.ok) throw new Error(`Campus API ${path} için ${response.status} döndürdü.`);
    return (await response.json()) as T;
  } finally {
    clearTimeout(timeout);
  }
}

export async function saveProfileToApi(profile: StudentProfile, profileId: string | null) {
  const payload = await apiRequest<{ profile_id: string }>(
    profileId ? `/profiles/${profileId}` : '/profiles',
    {
      method: profileId ? 'PUT' : 'POST',
      body: JSON.stringify(toProfileRequest(profile)),
    }
  );
  return payload.profile_id;
}

export async function fetchSavedEventIds(profileId: string) {
  const payload = await apiRequest<{ events: { event_id: string }[] }>(
    `/profiles/${profileId}/saved-events`
  );
  return payload.events.map((event) => `event-${event.event_id}`);
}

type ApiEvent = {
  event_id: string;
  club_name: string;
  title: string;
  description: string;
  category: string;
  event_type: string;
  date: string;
  time: string;
  location: string;
  location_type: CampusEvent['participationMode'];
  target_interests: string;
  target_goals: string;
  fee_type: CampusEvent['feeType'];
  language: CampusEvent['language'];
};

export async function fetchEventCatalog() {
  const payload = await apiRequest<{ events: ApiEvent[] }>('/events');
  const fallbackById = new Map(fallbackEvents.map((event) => [event.id, event]));

  return payload.events.flatMap((event) => {
    const fallback = fallbackById.get(`event-${event.event_id}`);
    if (!fallback) return [];
    const parsedDate = new Date(`${event.date}T12:00:00`);
    const dateLabel = Number.isNaN(parsedDate.getTime())
      ? fallback.dateLabel
      : parsedDate.toLocaleDateString('tr-TR', { day: 'numeric', month: 'long' });

    return [{
      ...fallback,
      title: event.title,
      clubName: event.club_name,
      description: event.description,
      dateLabel,
      time: event.time || fallback.time,
      location: event.location || fallback.location,
      participationMode: event.location_type,
      feeType: event.fee_type,
      language: event.language,
      interestIds: event.target_interests.split(';').filter(Boolean),
      goalIds: event.target_goals.split(';').filter(Boolean),
    } satisfies CampusEvent];
  });
}

export async function recordInteraction(
  profileId: string,
  eventId: string,
  action: InteractionAction,
  dwellMs?: number
) {
  return apiRequest('/interactions', {
    method: 'POST',
    body: JSON.stringify({
      profile_id: profileId,
      event_id: eventId.replace(/^event-/, ''),
      action,
      dwell_ms: dwellMs,
    }),
  });
}

export async function fetchSavedProfileRecommendations(profileId: string) {
  return apiRequest<RecommendationResponse>(`/recommendations/profile/${profileId}`, {
    method: 'POST',
  });
}

export type RecommendationResponse = {
  recommendations: {
    event: { event_id: string };
    score: number;
    reasons: string[];
  }[];
};

export async function fetchProfileRecommendations(profile: StudentProfile) {
  return apiRequest<RecommendationResponse>('/recommendations/profile', {
    method: 'POST',
    body: JSON.stringify(toProfileRequest(profile)),
  });
}
