import { createContext, PropsWithChildren, useContext, useState } from 'react';

import { RecommendationOverride } from '@/services/recommendations-api';

type AppContextValue = {
  profile: StudentProfile | null;
  saveProfile: (profile: StudentProfile) => void;
  recommendationOverrides: Record<string, RecommendationOverride>;
  setRecommendationOverrides: (overrides: Record<string, RecommendationOverride>) => void;
  savedEventIds: string[];
  toggleSavedEvent: (eventId: string) => void;
};

export type StudentProfile = {
  schemaVersion: '2.0';
  educationReferenceVersion: string;
  displayName: string;
  universityId: string;
  universityName: string;
  programId: string;
  programName: string;
  educationLevel: 'associate' | 'bachelor' | 'master' | 'doctorate';
  programDuration: number;
  classYear: string;
  interestIds: string[];
  participationGoalIds: string[];
  participationModes: string[];
  feePreference: string;
  languagePreference: string;
  campusId: string | null;
};

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ children }: PropsWithChildren) {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [recommendationOverrides, setRecommendationOverrides] = useState<
    Record<string, RecommendationOverride>
  >({});
  const [savedEventIds, setSavedEventIds] = useState<string[]>(['event-2']);

  const toggleSavedEvent = (eventId: string) => {
    setSavedEventIds((current) =>
      current.includes(eventId) ? current.filter((id) => id !== eventId) : [...current, eventId]
    );
  };

  return (
    <AppContext.Provider
      value={{
        profile,
        saveProfile: setProfile,
        recommendationOverrides,
        setRecommendationOverrides,
        savedEventIds,
        toggleSavedEvent,
      }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);

  if (!context) {
    throw new Error('useApp must be used inside AppProvider');
  }

  return context;
}
