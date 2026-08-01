import type { StudentProfile } from '@/context/app-context';

export type StoredProfile = StudentProfile & { profileId: string };

const API_URL = process.env.EXPO_PUBLIC_API_URL?.replace(/\/$/, '');

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

export async function persistProfile(profile: StudentProfile, profileId?: string | null) {
  if (!API_URL) return null;

  const response = await fetch(
    profileId ? `${API_URL}/profiles/${profileId}` : `${API_URL}/profiles`,
    {
      method: profileId ? 'PUT' : 'POST',
      headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: JSON.stringify(toProfileRequest(profile)),
    }
  );
  if (!response.ok) throw new Error(`Profile API returned ${response.status}`);
  const payload = (await response.json()) as { profile_id: string };
  return payload.profile_id;
}
