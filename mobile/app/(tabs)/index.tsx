import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useCallback, useEffect, useRef, useState } from 'react';
import { ActivityIndicator, Pressable, SafeAreaView, StyleSheet, Text, View } from 'react-native';

import { SwipeDeck } from '@/components/swipe-deck';
import { BrandColors, Fonts } from '@/constants/theme';
import { useApp } from '@/context/app-context';
import { events as fallbackEvents } from '@/mocks/events';
import { fetchFeed } from '@/services/feed-api';
import type { CampusEvent } from '@/types/event';
import { canonicalEventId, mapFeedItem } from '@/utils/api-event';
import { getPersonalizedEvents } from '@/utils/recommendations';

type QueueItem = { event: CampusEvent; feedToken?: string };

export default function DiscoverScreen() {
  const {
    profile,
    profileId,
    isHydrated,
    savedEventIds,
    saveProfile,
    registerFeedEvents,
    recordEventInteraction,
    toggleSavedEvent,
  } = useApp();
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [source, setSource] = useState<'loading' | 'live' | 'local' | 'empty'>('loading');
  const [retrying, setRetrying] = useState(false);
  const loadingRef = useRef(false);
  const shownAtRef = useRef(Date.now());
  const firstName = profile?.displayName.trim().split(/\s+/)[0] || 'Öğrenci';

  const setLocalQueue = useCallback(() => {
    const localEvents = getPersonalizedEvents(fallbackEvents, profile).map((event) => ({
      ...event,
      id: canonicalEventId(event.id),
    }));
    registerFeedEvents(localEvents);
    setQueue(localEvents.map((event) => ({ event })));
    setNextCursor(null);
    setHasMore(false);
    setSource(localEvents.length ? 'local' : 'empty');
  }, [profile, registerFeedEvents]);

  const loadFeed = useCallback(
    async (cursor: string | null, reset = false) => {
      if (!profileId || loadingRef.current) return;
      loadingRef.current = true;
      if (reset) setSource('loading');
      try {
        const payload = await fetchFeed(profileId, cursor, 20);
        if (!payload) {
          if (reset) setLocalQueue();
          return;
        }
        const mapped = payload.items.map(mapFeedItem);
        registerFeedEvents(mapped);
        const incoming = mapped.map((event) => ({ event, feedToken: payload.feed_token }));
        setQueue((current) => {
          const base = reset ? [] : current;
          const known = new Set(base.map((item) => item.event.id));
          return [...base, ...incoming.filter((item) => !known.has(item.event.id))];
        });
        setNextCursor(payload.next_cursor);
        setHasMore(payload.has_more);
        setSource(incoming.length || !reset ? 'live' : 'empty');
      } catch (error) {
        console.warn('Canlı feed alınamadı.', error);
        if (reset) setLocalQueue();
      } finally {
        loadingRef.current = false;
      }
    },
    [profileId, registerFeedEvents, setLocalQueue]
  );

  useEffect(() => {
    if (!isHydrated) return;
    if (profileId) void loadFeed(null, true);
    else setLocalQueue();
  }, [isHydrated, loadFeed, profileId, setLocalQueue]);

  useEffect(() => {
    shownAtRef.current = Date.now();
    if (queue.length <= 5 && hasMore && nextCursor && !loadingRef.current) {
      void loadFeed(nextCursor);
    }
  }, [hasMore, loadFeed, nextCursor, queue]);

  const consume = (action: 'like' | 'skip') => {
    const current = queue[0];
    if (!current) return;
    const dwellMs = Date.now() - shownAtRef.current;
    setQueue((items) => items.slice(1));
    void recordEventInteraction(current.event.id, action, {
      dwellMs,
      feedToken: current.feedToken,
    });
  };

  const openDetail = () => {
    const current = queue[0];
    if (!current) return;
    void recordEventInteraction(current.event.id, 'view_detail', {
      dwellMs: Date.now() - shownAtRef.current,
      feedToken: current.feedToken,
    });
    router.push({ pathname: '/event/[id]', params: { id: current.event.id } });
  };

  const retryLiveFeed = async () => {
    setRetrying(true);
    try {
      if (profileId) await loadFeed(null, true);
      else if (profile) await saveProfile(profile);
    } finally {
      setRetrying(false);
    }
  };

  const current = queue[0];

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.content}>
        <View style={styles.header}>
          <View>
            <Text style={styles.eyebrow}>CAMPUSMATCH AI</Text>
            <Text style={styles.greeting}>Merhaba {firstName}</Text>
          </View>
          <Pressable accessibilityLabel="Profili düzenle" onPress={() => router.push('/profile-setup')} style={styles.profileButton}>
            <Ionicons color={BrandColors.primary} name="person-outline" size={22} />
          </Pressable>
        </View>

        <View style={styles.sourceRow}>
          <View style={[styles.sourceDot, source === 'live' && styles.sourceDotLive]} />
          <Text style={styles.sourceText}>
            {source === 'live' ? 'Canlı kart kuyruğu' : source === 'local' ? 'Çevrim dışı örnek kartlar' : 'Kartlar hazırlanıyor'}
          </Text>
          {source === 'live' ? <Text style={styles.queueCount}>{queue.length} kart</Text> : null}
          {source === 'local' ? (
            <Pressable
              accessibilityLabel="Canlı kartları tekrar yükle"
              accessibilityRole="button"
              disabled={retrying}
              hitSlop={8}
              onPress={() => void retryLiveFeed()}
              style={styles.sourceRetry}>
              {retrying
                ? <ActivityIndicator color={BrandColors.primary} size="small" />
                : <Ionicons color={BrandColors.primary} name="refresh" size={17} />}
            </Pressable>
          ) : null}
        </View>

        {source === 'loading' || !isHydrated ? (
          <View style={styles.center}>
            <ActivityIndicator color={BrandColors.primary} size="large" />
            <Text style={styles.loadingText}>Sana uygun kartlar hazırlanıyor…</Text>
          </View>
        ) : current ? (
          <SwipeDeck
            event={current.event}
            isSaved={savedEventIds.includes(current.event.id)}
            nextEvent={queue[1]?.event}
            onDetail={openDetail}
            onLike={() => consume('like')}
            onSave={() => toggleSavedEvent(current.event.id, current.feedToken)}
            onSkip={() => consume('skip')}
          />
        ) : (
          <View style={styles.center}>
            <View style={styles.emptyIcon}><Ionicons color={BrandColors.primary} name="checkmark-done" size={32} /></View>
            <Text style={styles.emptyTitle}>Şimdilik tüm kartları gördün</Text>
            <Text style={styles.emptyText}>Yeni etkinlikler eklendiğinde kuyruğun burada yenilenecek.</Text>
            <Pressable accessibilityLabel="Kart kuyruğunu yenile" accessibilityRole="button" onPress={() => (profileId ? loadFeed(null, true) : setLocalQueue())} style={styles.retryButton}>
              <Text style={styles.retryText}>Kuyruğu yenile</Text>
            </Pressable>
          </View>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { backgroundColor: BrandColors.background, flex: 1 },
  content: { flex: 1, paddingHorizontal: 20, paddingTop: 14 },
  header: { alignItems: 'center', flexDirection: 'row', justifyContent: 'space-between' },
  eyebrow: { color: BrandColors.primary, fontFamily: Fonts.rounded, fontSize: 11, fontWeight: '800', letterSpacing: 1.5 },
  greeting: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 26, fontWeight: '800', marginTop: 3 },
  profileButton: { alignItems: 'center', backgroundColor: BrandColors.primarySoft, borderRadius: 22, height: 44, justifyContent: 'center', width: 44 },
  sourceRow: { alignItems: 'center', flexDirection: 'row', marginTop: 14 },
  sourceDot: { backgroundColor: BrandColors.placeholder, borderRadius: 4, height: 7, marginRight: 6, width: 7 },
  sourceDotLive: { backgroundColor: '#2C9A68' },
  sourceText: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 11, fontWeight: '700' },
  queueCount: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 11, marginLeft: 'auto' },
  sourceRetry: { alignItems: 'center', height: 30, justifyContent: 'center', marginLeft: 'auto', width: 30 },
  center: { alignItems: 'center', flex: 1, justifyContent: 'center', paddingBottom: 70, paddingHorizontal: 28 },
  loadingText: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 14, marginTop: 14 },
  emptyIcon: { alignItems: 'center', backgroundColor: BrandColors.primarySoft, borderRadius: 32, height: 64, justifyContent: 'center', marginBottom: 18, width: 64 },
  emptyTitle: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 20, fontWeight: '800', textAlign: 'center' },
  emptyText: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 14, lineHeight: 21, marginTop: 8, textAlign: 'center' },
  retryButton: { backgroundColor: BrandColors.primary, borderRadius: 16, marginTop: 20, paddingHorizontal: 20, paddingVertical: 13 },
  retryText: { color: BrandColors.surface, fontFamily: Fonts.rounded, fontSize: 14, fontWeight: '800' },
});
