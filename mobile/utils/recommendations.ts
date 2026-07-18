import type { StudentProfile } from '@/context/app-context';
import { interestGroups } from '@/data/profile-options';
import type { RecommendationOverride } from '@/services/recommendations-api';
import type { CampusEvent } from '@/types/event';

const interestLabels = Object.fromEntries(
  interestGroups.flatMap((group) => group.options.map((option) => [option.id, option.label]))
);

export function personalizeEvent(event: CampusEvent, profile: StudentProfile | null) {
  if (!profile) return event;

  const matchingInterests = profile.interestIds.filter((id) => event.interestIds.includes(id));
  const matchingGoals = profile.participationGoalIds.filter((id) => event.goalIds.includes(id));
  const matchesMode = profile.participationModes.includes(event.participationMode);
  const matchesFee = profile.feePreference !== 'free_only' || event.feeType === 'free';
  const matchesLanguage =
    profile.languagePreference === 'no_preference' ||
    profile.languagePreference === event.language ||
    event.language === 'mixed';

  const score = Math.min(
    98,
    48 +
      Math.min(matchingInterests.length * 12, 30) +
      Math.min(matchingGoals.length * 5, 10) +
      (matchesMode ? 5 : 0) +
      (matchesFee ? 3 : 0) +
      (matchesLanguage ? 2 : 0)
  );
  const reasons: string[] = [];

  if (matchingInterests.length > 0) {
    reasons.push(`${interestLabels[matchingInterests[0]] ?? 'İlgi alanın'} ile eşleşiyor`);
  }
  if (matchingGoals.length > 0) reasons.push('Katılım amacını destekliyor');
  if (matchesMode) reasons.push(`${event.locationType} katılım tercihine uyuyor`);
  if (profile.feePreference === 'free_only' && event.feeType === 'free') {
    reasons.push('Ücretsiz etkinlik tercihine uyuyor');
  }

  return { ...event, matchScore: score, reasons: reasons.length > 0 ? reasons : event.reasons };
}

export function getPersonalizedEvents(events: CampusEvent[], profile: StudentProfile | null) {
  return events
    .map((event) => personalizeEvent(event, profile))
    .sort((first, second) => second.matchScore - first.matchScore);
}

export function applyRecommendationOverrides(
  events: CampusEvent[],
  overrides: Record<string, RecommendationOverride>
) {
  return events
    .map((event) => {
      const override = overrides[event.id];
      return override
        ? { ...event, matchScore: Math.round(override.score), reasons: override.reasons }
        : event;
    })
    .sort((first, second) => second.matchScore - first.matchScore);
}
