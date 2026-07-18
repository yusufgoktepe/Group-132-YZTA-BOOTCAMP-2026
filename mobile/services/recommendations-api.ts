import type { StudentProfile } from '@/context/app-context';

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

const API_URL = process.env.EXPO_PUBLIC_API_URL?.replace(/\/$/, '');

export async function fetchRecommendationOverrides(profile: StudentProfile) {
  if (!API_URL) return null;

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5000);
  const requestBody = {
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

  try {
    const response = await fetch(`${API_URL}/recommendations/profile`, {
      method: 'POST',
      headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
      signal: controller.signal,
    });

    if (!response.ok) throw new Error(`Recommendation API returned ${response.status}`);

    const payload = (await response.json()) as RecommendationResponse;
    return Object.fromEntries(
      payload.recommendations.map((item) => [
        `event-${item.event.event_id}`,
        { score: item.score, reasons: item.reasons },
      ])
    ) as Record<string, RecommendationOverride>;
  } catch (error) {
    console.warn('Recommendation API kullanılamıyor, yerel öneriler gösteriliyor.', error);
    return null;
  } finally {
    clearTimeout(timeout);
  }
}
