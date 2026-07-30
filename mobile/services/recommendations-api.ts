import type { StudentProfile } from '@/context/app-context';
import {
  fetchProfileRecommendations,
  fetchSavedProfileRecommendations,
  type RecommendationResponse,
} from '@/services/campus-api';

export type RecommendationOverride = {
  score: number;
  reasons: string[];
};

export async function fetchRecommendationOverrides(
  profile: StudentProfile,
  profileId: string | null
) {

  try {
    const payload: RecommendationResponse = profileId
      ? await fetchSavedProfileRecommendations(profileId)
      : await fetchProfileRecommendations(profile);
    return Object.fromEntries(
      payload.recommendations.map((item) => [
        `event-${item.event.event_id}`,
        { score: item.score, reasons: item.reasons },
      ])
    ) as Record<string, RecommendationOverride>;
  } catch (error) {
    console.warn('Recommendation API kullanılamıyor, yerel öneriler gösteriliyor.', error);
    return null;
  }
}
