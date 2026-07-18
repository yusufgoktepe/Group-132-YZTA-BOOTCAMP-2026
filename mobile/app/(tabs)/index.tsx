import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useEffect, useState } from 'react';
import { Pressable, SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';

import { EventCard } from '@/components/event-card';
import { BrandColors, Fonts } from '@/constants/theme';
import { useApp } from '@/context/app-context';
import { eventCategories, events } from '@/mocks/events';
import { fetchRecommendationOverrides } from '@/services/recommendations-api';
import { applyRecommendationOverrides, getPersonalizedEvents } from '@/utils/recommendations';

export default function DiscoverScreen() {
  const [selectedCategory, setSelectedCategory] = useState('Tümü');
  const [recommendationSource, setRecommendationSource] = useState<'local' | 'checking' | 'live'>(
    'local'
  );
  const {
    profile,
    recommendationOverrides,
    setRecommendationOverrides,
    savedEventIds,
    toggleSavedEvent,
  } = useApp();
  const firstName = profile?.displayName.trim().split(/\s+/)[0] || 'Öğrenci';
  const personalizedEvents = applyRecommendationOverrides(
    getPersonalizedEvents(events, profile),
    recommendationOverrides
  );
  const visibleEvents = selectedCategory === 'Tümü'
    ? personalizedEvents
    : personalizedEvents.filter((event) => event.category === selectedCategory);

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
    fetchRecommendationOverrides(profile).then((overrides) => {
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
  }, [profile, setRecommendationOverrides]);

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

        {visibleEvents.map((event) => (
          <EventCard
            event={event}
            isSaved={savedEventIds.includes(event.id)}
            key={event.id}
            onPress={() => router.push({ pathname: '/event/[id]', params: { id: event.id } })}
            onToggleSaved={() => toggleSavedEvent(event.id)}
          />
        ))}
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
});
