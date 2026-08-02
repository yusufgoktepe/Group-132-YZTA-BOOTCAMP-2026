import type { StudentProfile } from '@/context/app-context';
import { apiRequest, isApiConfigured } from '@/services/api-client';
import { toProfileRequest } from '@/services/profiles-api';
import { canonicalEventId } from '@/utils/api-event';

export type RecommendationOverride = {
  score: number;
  reasons: string[];
};

type RecommendationResponse = {
  recommendations: {
    event: { event_id: string };
    score: number;
    reasons: string[];
  }[];
};

export async function fetchRecommendationOverrides(profile: StudentProfile) {
  if (!isApiConfigured()) return null;
  const requestBody = toProfileRequest(profile);

  try {
    const payload = await apiRequest<RecommendationResponse>('/recommendations/profile', {
      method: 'POST',
      body: JSON.stringify(requestBody),
    }, 'Öneriler alınamadı.');
    return Object.fromEntries(
      payload.recommendations.map((item) => [
        canonicalEventId(item.event.event_id),
        { score: item.score, reasons: item.reasons },
      ])
    ) as Record<string, RecommendationOverride>;
  } catch (error) {
    console.warn('Recommendation API kullanılamıyor, yerel öneriler gösteriliyor.', error);
    return null;
  }
}
