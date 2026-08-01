import AsyncStorage from '@react-native-async-storage/async-storage';

import type { StudentProfile } from '@/context/app-context';
import { sendInteraction, type PendingInteraction } from '@/services/interactions-api';

const SESSION_KEY = '@campusmatch/session-v1';
const INTERACTION_QUEUE_KEY = '@campusmatch/interaction-queue-v1';

export type StoredSession = {
  profile: StudentProfile | null;
  profileId: string | null;
};

export async function loadSession(): Promise<StoredSession> {
  const value = await AsyncStorage.getItem(SESSION_KEY);
  return value ? (JSON.parse(value) as StoredSession) : { profile: null, profileId: null };
}

export async function storeSession(session: StoredSession) {
  await AsyncStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export async function loadPendingInteractions(): Promise<PendingInteraction[]> {
  const value = await AsyncStorage.getItem(INTERACTION_QUEUE_KEY);
  return value ? (JSON.parse(value) as PendingInteraction[]) : [];
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
