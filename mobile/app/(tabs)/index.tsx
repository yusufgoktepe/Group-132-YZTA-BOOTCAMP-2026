import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useEffect, useState } from 'react';
import { Pressable, SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';

import { EventCard } from '@/components/event-card';
import { BrandColors, Fonts } from '@/constants/theme';
import { useApp } from '@/context/app-context';
import { fetchRecommendationOverrides } from '@/services/recommendations-api';
import { applyRecommendationOverrides, getPersonalizedEvents } from '@/utils/recommendations';

export default function DiscoverScreen() {
  const [selectedCategory, setSelectedCategory] = useState('Tümü');
  const [skippedEventIds, setSkippedEventIds] = useState<string[]>([]);
  const [recommendationRequest, setRecommendationRequest] = useState(0);
  const [recommendationSource, setRecommendationSource] = useState<'local' | 'checking' | 'live'>(
    'local'
  );
  const {
    profile,
    profileId,
    catalogEvents,
    catalogStatus,
    retryCatalog,
    recommendationOverrides,
    setRecommendationOverrides,
    savedEventIds,
    toggleSavedEvent,
    recordEventInteraction,
  } = useApp();
  const eventCategories = ['Tümü', ...new Set(catalogEvents.map((event) => event.category))];
  const firstName = profile?.displayName.trim().split(/\s+/)[0] || 'Öğrenci';
  const personalizedEvents = applyRecommendationOverrides(
    getPersonalizedEvents(catalogEvents, profile),
    recommendationOverrides
  );
  const categoryEvents = selectedCategory === 'Tümü'
    ? personalizedEvents
    : personalizedEvents.filter((event) => event.category === selectedCategory);
  const visibleEvents = categoryEvents.filter((event) => !skippedEventIds.includes(event.id));

  useEffect(() => {
    let isActive = true;

    if (!profile) {
      setRecommendationSource('local');
      setRecommendationOverrides({});
      return () => {
        isActive = false;
      };
    }

    setRecommendationSource('checking');
    fetchRecommendationOverrides(profile, profileId).then((overrides) => {
      if (!isActive) return;
      if (overrides) {
        setRecommendationOverrides(overrides);
        setRecommendationSource('live');
      } else {
        setRecommendationOverrides({});
        setRecommendationSource('local');
      }
    });

    return () => {
      isActive = false;
    };
  }, [profile, profileId, recommendationRequest, setRecommendationOverrides]);

  const retryConnection = () => {
    retryCatalog();
    setRecommendationRequest((current) => current + 1);
  };

  const skipEvent = (eventId: string) => {
    setSkippedEventIds((current) => [...new Set([...current, eventId])]);
    recordEventInteraction(eventId, 'skip');
  };

  const isCheckingConnection = catalogStatus === 'loading' || recommendationSource === 'checking';
  const isUsingFallback = catalogStatus === 'fallback' || recommendationSource === 'local';

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <View>
            <Text style={styles.eyebrow}>CAMPUSMATCH AI</Text>
            <Text style={styles.greeting}>Merhaba {firstName}</Text>
          </View>
          <Pressable accessibilityLabel="Profili düzenle" onPress={() => router.push('/profile-setup')} style={styles.profileButton}>
            <Ionicons color={BrandColors.primary} name="person-outline" size={22} />
          </Pressable>
        </View>

        <View style={styles.intro}>
          <View style={styles.introIcon}>
            <Ionicons color={BrandColors.primary} name="sparkles" size={20} />
          </View>
          <View style={styles.introCopy}>
            <Text style={styles.introTitle}>Senin için seçtik</Text>
            <Text style={styles.introText}>Profiline göre eşleşen kampüs etkinliklerini keşfet.</Text>
            <View style={styles.sourceRow}>
              <View
                style={[
                  styles.sourceDot,
                  recommendationSource === 'live' && styles.sourceDotLive,
                ]}
              />
              <Text style={styles.sourceText}>
                {recommendationSource === 'live'
                  ? 'Canlı öneri'
                  : recommendationSource === 'checking'
                    ? 'Bağlantı kontrol ediliyor'
                    : 'Yerel öneri'}
              </Text>
            </View>
          </View>
        </View>

        <ScrollView contentContainerStyle={styles.categories} horizontal showsHorizontalScrollIndicator={false}>
          {eventCategories.map((category) => {
            const isSelected = category === selectedCategory;
            return (
              <Pressable key={category} onPress={() => setSelectedCategory(category)} style={[styles.category, isSelected && styles.selectedCategory]}>
                <Text style={[styles.categoryText, isSelected && styles.selectedCategoryText]}>{category}</Text>
              </Pressable>
            );
          })}
        </ScrollView>

        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Önerilen etkinlikler</Text>
          <Text style={styles.resultCount}>{visibleEvents.length} sonuç</Text>
        </View>

        {isCheckingConnection ? (
          <View accessibilityLiveRegion="polite" style={styles.statusCard}>
            <View style={[styles.statusIcon, styles.statusIconLoading]}>
              <Ionicons color={BrandColors.primary} name="cloud-download-outline" size={20} />
            </View>
            <View style={styles.statusCopy}>
              <Text style={styles.statusTitle}>Öneriler güncelleniyor</Text>
              <Text style={styles.statusText}>Bağlantıyı kontrol ederken etkinlikleri hazırlıyoruz.</Text>
            </View>
          </View>
        ) : isUsingFallback ? (
          <View accessibilityLiveRegion="polite" style={[styles.statusCard, styles.statusCardWarning]}>
            <View style={[styles.statusIcon, styles.statusIconWarning]}>
              <Ionicons color={BrandColors.accentDark} name="cloud-offline-outline" size={20} />
            </View>
            <View style={styles.statusCopy}>
              <Text style={styles.statusTitle}>Demo etkinlikleri gösteriliyor</Text>
              <Text style={styles.statusText}>Sunucuya ulaşılamadı. Keşfe kesintisiz devam edebilirsin.</Text>
            </View>
            <Pressable accessibilityLabel="Bağlantıyı tekrar dene" hitSlop={8} onPress={retryConnection} style={styles.retryButton}>
              <Ionicons color={BrandColors.accentDark} name="refresh" size={18} />
            </Pressable>
          </View>
        ) : null}

        {visibleEvents.length === 0 ? (
          <View style={styles.emptyState}>
            <View style={styles.emptyIcon}>
              <Ionicons color={BrandColors.primary} name="compass-outline" size={26} />
            </View>
            <Text style={styles.emptyTitle}>
              {categoryEvents.length > 0 ? 'Bu önerilerin hepsini geçtin' : 'Bu kategoride etkinlik bulunamadı'}
            </Text>
            <Text style={styles.emptyText}>
              {categoryEvents.length > 0
                ? 'İstersen geçtiğin kartları yeniden inceleyebilirsin.'
                : 'Diğer önerilere dönerek yeni etkinlikleri keşfedebilirsin.'}
            </Text>
            <Pressable
              onPress={() => {
                if (categoryEvents.length > 0) setSkippedEventIds([]);
                else setSelectedCategory('Tümü');
              }}
              style={styles.emptyButton}>
              <Text style={styles.emptyButtonText}>
                {categoryEvents.length > 0 ? 'Geçilenleri geri getir' : 'Tüm etkinlikleri göster'}
              </Text>
            </Pressable>
          </View>
        ) : (
          visibleEvents.map((event) => (
            <EventCard
              event={event}
              isSaved={savedEventIds.includes(event.id)}
              key={event.id}
              onPress={() => router.push({ pathname: '/event/[id]', params: { id: event.id } })}
              onSkip={() => skipEvent(event.id)}
              onToggleSaved={() => toggleSavedEvent(event.id)}
            />
          ))
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { backgroundColor: BrandColors.background, flex: 1 },
  content: { paddingBottom: 30, paddingHorizontal: 20, paddingTop: 14 },
  header: { alignItems: 'center', flexDirection: 'row', justifyContent: 'space-between' },
  eyebrow: { color: BrandColors.primary, fontFamily: Fonts.rounded, fontSize: 11, fontWeight: '800', letterSpacing: 1.5 },
  greeting: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 26, fontWeight: '800', marginTop: 3 },
  profileButton: { alignItems: 'center', backgroundColor: BrandColors.primarySoft, borderRadius: 22, height: 44, justifyContent: 'center', width: 44 },
  intro: { alignItems: 'center', backgroundColor: BrandColors.surface, borderColor: BrandColors.border, borderRadius: 20, borderWidth: 1, flexDirection: 'row', marginTop: 24, padding: 15 },
  introIcon: { alignItems: 'center', backgroundColor: BrandColors.primarySoft, borderRadius: 16, height: 46, justifyContent: 'center', width: 46 },
  introCopy: { flex: 1, marginLeft: 12 },
  introTitle: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 16, fontWeight: '800' },
  introText: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 13, lineHeight: 18, marginTop: 3 },
  sourceRow: { alignItems: 'center', flexDirection: 'row', gap: 6, marginTop: 7 },
  sourceDot: { backgroundColor: BrandColors.placeholder, borderRadius: 4, height: 7, width: 7 },
  sourceDotLive: { backgroundColor: '#2C9A68' },
  sourceText: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 10, fontWeight: '700' },
  categories: { gap: 9, paddingVertical: 20 },
  category: { backgroundColor: BrandColors.surface, borderColor: BrandColors.border, borderRadius: 999, borderWidth: 1, paddingHorizontal: 17, paddingVertical: 10 },
  selectedCategory: { backgroundColor: BrandColors.primary, borderColor: BrandColors.primary },
  categoryText: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 13, fontWeight: '700' },
  selectedCategoryText: { color: BrandColors.surface },
  sectionHeader: { alignItems: 'center', flexDirection: 'row', justifyContent: 'space-between', marginBottom: 13 },
  sectionTitle: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 19, fontWeight: '800' },
  resultCount: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 12 },
  statusCard: { alignItems: 'center', backgroundColor: BrandColors.primarySoft, borderColor: BrandColors.border, borderRadius: 18, borderWidth: 1, flexDirection: 'row', marginBottom: 14, padding: 13 },
  statusCardWarning: { backgroundColor: BrandColors.accentSoft, borderColor: BrandColors.accentBorder },
  statusIcon: { alignItems: 'center', borderRadius: 13, height: 40, justifyContent: 'center', width: 40 },
  statusIconLoading: { backgroundColor: BrandColors.surface },
  statusIconWarning: { backgroundColor: '#FFF8EC' },
  statusCopy: { flex: 1, marginLeft: 11 },
  statusTitle: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 13, fontWeight: '800' },
  statusText: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 11, lineHeight: 16, marginTop: 2 },
  retryButton: { alignItems: 'center', borderColor: BrandColors.accentBorder, borderRadius: 12, borderWidth: 1, height: 38, justifyContent: 'center', marginLeft: 8, width: 38 },
  emptyState: { alignItems: 'center', backgroundColor: BrandColors.surface, borderColor: BrandColors.border, borderRadius: 22, borderWidth: 1, paddingHorizontal: 24, paddingVertical: 32 },
  emptyIcon: { alignItems: 'center', backgroundColor: BrandColors.primarySoft, borderRadius: 22, height: 50, justifyContent: 'center', width: 50 },
  emptyTitle: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 16, fontWeight: '800', marginTop: 14, textAlign: 'center' },
  emptyText: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 12, lineHeight: 18, marginTop: 6, textAlign: 'center' },
  emptyButton: { backgroundColor: BrandColors.primary, borderRadius: 14, marginTop: 18, paddingHorizontal: 18, paddingVertical: 11 },
  emptyButtonText: { color: BrandColors.surface, fontFamily: Fonts.rounded, fontSize: 12, fontWeight: '800' },
});
