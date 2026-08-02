import { createContext, PropsWithChildren, useCallback, useContext, useEffect, useState } from 'react';

import {
  enqueueInteraction,
  flushPendingInteractions,
  loadSavedState,
  loadSession,
  storeSavedState,
  storeSession,
} from '@/services/device-storage';
import { fetchSavedEvents, sendInteraction, type InteractionAction } from '@/services/interactions-api';
import { RecommendationOverride } from '@/services/recommendations-api';
import { persistProfile } from '@/services/profiles-api';
import type { CampusEvent } from '@/types/event';
import { canonicalEventId, mapApiEvent } from '@/utils/api-event';

type AppContextValue = {
  profile: StudentProfile | null;
  profileId: string | null;
  isHydrated: boolean;
  saveProfile: (profile: StudentProfile) => Promise<string | null>;
  recommendationOverrides: Record<string, RecommendationOverride>;
  setRecommendationOverrides: (overrides: Record<string, RecommendationOverride>) => void;
  savedEventIds: string[];
  savedEvents: CampusEvent[];
  feedEvents: Record<string, CampusEvent>;
  registerFeedEvents: (events: CampusEvent[]) => void;
  recordEventInteraction: (
    eventId: string,
    action: InteractionAction,
    options?: { dwellMs?: number; feedToken?: string }
  ) => Promise<void>;
  toggleSavedEvent: (eventId: string, feedToken?: string) => void;
  refreshSavedEvents: () => Promise<void>;
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
  const [isHydrated, setIsHydrated] = useState(false);
  const [recommendationOverrides, setRecommendationOverrides] = useState<
    Record<string, RecommendationOverride>
  >({});
  const [savedEventIds, setSavedEventIds] = useState<string[]>([]);
  const [savedEvents, setSavedEvents] = useState<CampusEvent[]>([]);
  const [feedEvents, setFeedEvents] = useState<Record<string, CampusEvent>>({});

  const registerFeedEvents = useCallback((nextEvents: CampusEvent[]) => {
    setFeedEvents((current) => ({
      ...current,
      ...Object.fromEntries(nextEvents.map((event) => [event.id, event])),
    }));
  }, []);

  useEffect(() => {
    Promise.all([loadSession(), loadSavedState()])
      .then(([session, savedState]) => {
        const restoredEvents = savedState.events.map((event) => ({
          ...event,
          id: canonicalEventId(event.id),
        }));
        const restoredIds = [...new Set(savedState.eventIds.map(canonicalEventId))];
        setProfile(session.profile);
        setProfileId(session.profileId);
        setSavedEventIds(restoredIds);
        setSavedEvents(restoredEvents);
        registerFeedEvents(restoredEvents);
        void storeSavedState({ eventIds: restoredIds, events: restoredEvents });
        return flushPendingInteractions();
      })
      .catch((error) => console.warn('Cihaz oturumu yüklenemedi.', error))
      .finally(() => setIsHydrated(true));
  }, [registerFeedEvents]);

  const refreshSavedEvents = useCallback(async () => {
    if (!profileId) return;
    try {
      const payload = await fetchSavedEvents(profileId);
      if (!payload) return;
      const mapped = payload.events.map((event) => mapApiEvent(event));
      setSavedEvents(mapped);
      setSavedEventIds(mapped.map((event) => event.id));
      registerFeedEvents(mapped);
      await storeSavedState({ eventIds: mapped.map((event) => event.id), events: mapped });
    } catch (error) {
      console.warn('Kaydedilen etkinlikler alınamadı.', error);
    }
  }, [profileId, registerFeedEvents]);

  const recordEventInteraction = useCallback(async (
    eventId: string,
    action: InteractionAction,
    options?: { dwellMs?: number; feedToken?: string }
  ) => {
    if (!profileId) return;
    const interaction = {
      profileId,
      eventId,
      action,
      dwellMs: options?.dwellMs,
      feedToken: options?.feedToken,
      interactionKey: `${profileId}-${eventId}-${action}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    };
    try {
      const response = await sendInteraction(interaction);
      if (!response) await enqueueInteraction(interaction);
      else await flushPendingInteractions();
    } catch {
      await enqueueInteraction(interaction);
    }
  }, [profileId]);

  const toggleSavedEvent = useCallback((eventId: string, feedToken?: string) => {
    const willSave = !savedEventIds.includes(eventId);
    const nextIds = willSave
      ? [...savedEventIds, eventId]
      : savedEventIds.filter((id) => id !== eventId);
    const nextEvents = willSave && feedEvents[eventId]
      ? [feedEvents[eventId], ...savedEvents.filter((item) => item.id !== eventId)]
      : savedEvents.filter((item) => item.id !== eventId);
    setSavedEventIds(nextIds);
    setSavedEvents(nextEvents);
    if (willSave && feedEvents[eventId]) {
      registerFeedEvents([feedEvents[eventId]]);
    }
    void storeSavedState({ eventIds: nextIds, events: nextEvents });
    void recordEventInteraction(eventId, willSave ? 'save' : 'unsave', { feedToken });
  }, [feedEvents, recordEventInteraction, registerFeedEvents, savedEventIds, savedEvents]);

  const saveProfile = async (nextProfile: StudentProfile) => {
    setProfile(nextProfile);
    try {
      const storedId = await persistProfile(nextProfile, profileId);
      if (storedId) {
        setProfileId(storedId);
        await storeSession({ profile: nextProfile, profileId: storedId });
        await flushPendingInteractions();
      } else {
        await storeSession({ profile: nextProfile, profileId });
      }
      return storedId;
    } catch (error) {
      console.warn('Profil backend üzerinde saklanamadı; yerel profil kullanılacak.', error);
      await storeSession({ profile: nextProfile, profileId });
      return null;
    }
  };

  useEffect(() => {
    if (profileId && isHydrated) void refreshSavedEvents();
  }, [isHydrated, profileId, refreshSavedEvents]);

  return (
    <AppContext.Provider
      value={{
        profile,
        profileId,
        isHydrated,
        saveProfile,
        recommendationOverrides,
        setRecommendationOverrides,
        savedEventIds,
        savedEvents,
        feedEvents,
        registerFeedEvents,
        recordEventInteraction,
        toggleSavedEvent,
        refreshSavedEvents,
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
