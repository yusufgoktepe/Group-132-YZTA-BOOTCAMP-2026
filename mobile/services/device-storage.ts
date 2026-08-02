import AsyncStorage from '@react-native-async-storage/async-storage';

import type { StudentProfile } from '@/context/app-context';
import { sendInteraction, type PendingInteraction } from '@/services/interactions-api';
import type { CampusEvent } from '@/types/event';

const SESSION_KEY = '@campusmatch/session-v1';
const INTERACTION_QUEUE_KEY = '@campusmatch/interaction-queue-v1';
const SAVED_STATE_KEY = '@campusmatch/saved-state-v1';

export type StoredSession = {
  profile: StudentProfile | null;
  profileId: string | null;
};

export type StoredSavedState = {
  eventIds: string[];
  events: CampusEvent[];
};

function parseStoredValue<T>(value: string | null, fallback: T): T {
  if (!value) return fallback;
  try {
    return JSON.parse(value) as T;
  } catch {
    return fallback;
  }
}

export async function loadSession(): Promise<StoredSession> {
  const value = await AsyncStorage.getItem(SESSION_KEY);
  const parsed = parseStoredValue<Partial<StoredSession>>(value, {});
  return {
    profile: parsed.profile ?? null,
    profileId: typeof parsed.profileId === 'string' ? parsed.profileId : null,
  };
}

export async function storeSession(session: StoredSession) {
  await AsyncStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export async function loadSavedState(): Promise<StoredSavedState> {
  const value = await AsyncStorage.getItem(SAVED_STATE_KEY);
  const parsed = parseStoredValue<Partial<StoredSavedState>>(value, {});
  return {
    eventIds: Array.isArray(parsed.eventIds) ? parsed.eventIds.filter((id): id is string => typeof id === 'string') : [],
    events: Array.isArray(parsed.events) ? parsed.events : [],
  };
}

export async function storeSavedState(state: StoredSavedState) {
  await AsyncStorage.setItem(SAVED_STATE_KEY, JSON.stringify(state));
}

export async function loadPendingInteractions(): Promise<PendingInteraction[]> {
  const value = await AsyncStorage.getItem(INTERACTION_QUEUE_KEY);
  const parsed = parseStoredValue<unknown>(value, []);
  return Array.isArray(parsed) ? parsed as PendingInteraction[] : [];
}

export async function enqueueInteraction(interaction: PendingInteraction) {
  const queued = await loadPendingInteractions();
  if (!queued.some((item) => item.interactionKey === interaction.interactionKey)) {
    queued.push(interaction);
    await AsyncStorage.setItem(INTERACTION_QUEUE_KEY, JSON.stringify(queued));
  }
}

export async function flushPendingInteractions() {
  const queued = await loadPendingInteractions();
  if (!queued.length) return 0;

  const remaining: PendingInteraction[] = [];
  let sent = 0;
  for (const interaction of queued) {
    try {
      const response = await sendInteraction(interaction);
      if (response) sent += 1;
      else remaining.push(interaction);
    } catch {
      remaining.push(interaction);
    }
  }
  await AsyncStorage.setItem(INTERACTION_QUEUE_KEY, JSON.stringify(remaining));
  return sent;
}
