import AsyncStorage from '@react-native-async-storage/async-storage';
import { createContext, PropsWithChildren, useContext, useEffect, useRef, useState } from 'react';

import { RecommendationOverride } from '@/services/recommendations-api';
import {
  fetchEventCatalog,
  fetchSavedEventIds,
  type InteractionAction,
  recordInteraction,
  saveProfileToApi,
} from '@/services/campus-api';
import { events as fallbackEvents } from '@/mocks/events';
import type { CampusEvent } from '@/types/event';

const PROFILE_KEY = 'campusmatch.profile.v2';
const PROFILE_ID_KEY = 'campusmatch.profile-id';
const SAVED_EVENTS_KEY = 'campusmatch.saved-events';

type AppContextValue = {
  profile: StudentProfile | null;
  profileId: string | null;
  isHydrated: boolean;
  catalogEvents: CampusEvent[];
  catalogStatus: 'loading' | 'live' | 'fallback';
  retryCatalog: () => void;
  saveProfile: (profile: StudentProfile) => void;
  recommendationOverrides: Record<string, RecommendationOverride>;
  setRecommendationOverrides: (overrides: Record<string, RecommendationOverride>) => void;
  savedEventIds: string[];
  toggleSavedEvent: (eventId: string) => void;
  recordEventInteraction: (eventId: string, action: InteractionAction) => void;
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
  const [profileId, setProfileId] = useState<string | null>(null);
  const profileSyncRef = useRef<Promise<string | null> | null>(null);
  const [isHydrated, setIsHydrated] = useState(false);
  const [catalogEvents, setCatalogEvents] = useState<CampusEvent[]>(fallbackEvents);
  const [catalogStatus, setCatalogStatus] = useState<'loading' | 'live' | 'fallback'>(
    'loading'
  );
  const [recommendationOverrides, setRecommendationOverrides] = useState<
    Record<string, RecommendationOverride>
  >({});
  const [savedEventIds, setSavedEventIds] = useState<string[]>([]);

  const loadCatalog = async () => {
    setCatalogStatus('loading');
    try {
      const remoteEvents = await fetchEventCatalog();
      if (remoteEvents.length === 0) {
        setCatalogEvents(fallbackEvents);
        setCatalogStatus('fallback');
        return;
      }
      setCatalogEvents(remoteEvents);
      setCatalogStatus('live');
    } catch (error) {
      console.warn('Etkinlik kataloğu alınamadı; demo verileri gösteriliyor.', error);
      setCatalogEvents(fallbackEvents);
      setCatalogStatus('fallback');
    }
  };

  useEffect(() => {
    let active = true;

    async function hydrate() {
      void loadCatalog();
      try {
        const entries = await AsyncStorage.multiGet([
          PROFILE_KEY,
          PROFILE_ID_KEY,
          SAVED_EVENTS_KEY,
        ]);
        const stored = Object.fromEntries(entries);
        const storedProfile = stored[PROFILE_KEY]
          ? (JSON.parse(stored[PROFILE_KEY]) as StudentProfile)
          : null;
        const storedProfileId = stored[PROFILE_ID_KEY] || null;
        const storedSavedIds = stored[SAVED_EVENTS_KEY]
          ? (JSON.parse(stored[SAVED_EVENTS_KEY]) as string[])
          : [];

        if (!active) return;
        setProfile(storedProfile);
        setProfileId(storedProfileId);
        setSavedEventIds(storedSavedIds);

        if (storedProfileId) {
          fetchSavedEventIds(storedProfileId)
            .then((remoteIds) => {
              if (!active) return;
              setSavedEventIds(remoteIds);
              return AsyncStorage.setItem(SAVED_EVENTS_KEY, JSON.stringify(remoteIds));
            })
            .catch(() => undefined);
        }
      } catch (error) {
        console.warn('Yerel profil bilgileri okunamadı.', error);
      } finally {
        if (active) setIsHydrated(true);
      }
    }

    void hydrate();
    return () => {
      active = false;
    };
  }, []);

  const saveProfile = (nextProfile: StudentProfile) => {
    setProfile(nextProfile);
    void AsyncStorage.setItem(PROFILE_KEY, JSON.stringify(nextProfile));

    const sync = saveProfileToApi(nextProfile, profileId)
      .then((remoteProfileId) => {
        setProfileId(remoteProfileId);
        return AsyncStorage.setItem(PROFILE_ID_KEY, remoteProfileId).then(
          () => remoteProfileId
        );
      })
      .catch((error) => {
        console.warn('Profil backend ile senkronlanamadı; yerel profil korunuyor.', error);
        return null;
      });
    profileSyncRef.current = sync;
  };

  const syncInteraction = async (eventId: string, action: InteractionAction) => {
    const remoteProfileId = profileId ?? (await profileSyncRef.current);
    if (!remoteProfileId) return;
    await recordInteraction(remoteProfileId, eventId, action);
  };

  const toggleSavedEvent = (eventId: string) => {
    const isSaved = savedEventIds.includes(eventId);
    const nextIds = isSaved
      ? savedEventIds.filter((id) => id !== eventId)
      : [...savedEventIds, eventId];
    setSavedEventIds(nextIds);
    void AsyncStorage.setItem(SAVED_EVENTS_KEY, JSON.stringify(nextIds));
    void syncInteraction(eventId, isSaved ? 'unsave' : 'save').catch((error) =>
        console.warn('Kaydetme hareketi backend ile senkronlanamadı.', error)
      );
  };

  const recordEventInteraction = (eventId: string, action: InteractionAction) => {
    void syncInteraction(eventId, action).catch((error) =>
      console.warn(`${action} hareketi backend ile senkronlanamadı.`, error)
    );
  };

  return (
    <AppContext.Provider
      value={{
        profile,
        profileId,
        isHydrated,
        catalogEvents,
        catalogStatus,
        retryCatalog: () => void loadCatalog(),
        saveProfile,
        recommendationOverrides,
        setRecommendationOverrides,
        savedEventIds,
        toggleSavedEvent,
        recordEventInteraction,
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
