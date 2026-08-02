import type { StudentProfile } from '@/context/app-context';
import { apiRequest, isApiConfigured } from '@/services/api-client';

export type StoredProfile = StudentProfile & { profileId: string };

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
  if (!isApiConfigured()) return null;
  const payload = await apiRequest<{ profile_id: string }>(
    profileId ? `/profiles/${profileId}` : '/profiles',
    {
      method: profileId ? 'PUT' : 'POST',
      body: JSON.stringify(toProfileRequest(profile)),
    },
    'Profil sunucuya kaydedilemedi.'
  );
  return payload.profile_id;
}
