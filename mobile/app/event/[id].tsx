import { Ionicons } from '@expo/vector-icons';
import { router, useLocalSearchParams } from 'expo-router';
import { Alert, Pressable, SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';

import { BrandColors, Fonts } from '@/constants/theme';
import { useApp } from '@/context/app-context';
import { events } from '@/mocks/events';
import { applyRecommendationOverrides, personalizeEvent } from '@/utils/recommendations';

export default function EventDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { profile, recommendationOverrides, savedEventIds, toggleSavedEvent } = useApp();
  const sourceEvent = events.find((item) => item.id === id);
  const event = sourceEvent
    ? applyRecommendationOverrides(
        [personalizeEvent(sourceEvent, profile)],
        recommendationOverrides
      )[0]
    : undefined;

  if (!event) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.notFound}>
          <Text style={styles.title}>Etkinlik bulunamadı</Text>
          <Pressable onPress={() => router.back()} style={styles.primaryButton}><Text style={styles.primaryButtonText}>Geri dön</Text></Pressable>
        </View>
      </SafeAreaView>
    );
  }

  const isSaved = savedEventIds.includes(event.id);

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.topBar}>
          <Pressable accessibilityLabel="Geri dön" onPress={() => router.back()} style={styles.iconButton}>
            <Ionicons color={BrandColors.text} name="arrow-back" size={22} />
          </Pressable>
          <Pressable accessibilityLabel={isSaved ? 'Kaydedilenlerden çıkar' : 'Etkinliği kaydet'} onPress={() => toggleSavedEvent(event.id)} style={styles.iconButton}>
            <Ionicons color={BrandColors.primary} name={isSaved ? 'bookmark' : 'bookmark-outline'} size={22} />
          </Pressable>
        </View>

        <View style={[styles.hero, { backgroundColor: event.color }]}>
          <Ionicons color={BrandColors.primary} name={event.icon} size={68} />
          <View style={styles.scoreBadge}>
            <Ionicons color={BrandColors.primary} name="sparkles" size={14} />
            <Text style={styles.scoreText}>%{event.matchScore} profil eşleşmesi</Text>
          </View>
        </View>

        <Text style={styles.club}>{event.clubName}</Text>
        <Text style={styles.title}>{event.title}</Text>
        <View style={styles.infoGrid}>
          <InfoItem icon="calendar-outline" label="Tarih" value={event.dateLabel} />
          <InfoItem icon="time-outline" label="Saat" value={event.time} />
          <InfoItem icon="location-outline" label="Konum" value={event.locationType} />
          <InfoItem icon="people-outline" label="Tür" value={event.format} />
        </View>

        <Text style={styles.sectionTitle}>Etkinlik hakkında</Text>
        <Text style={styles.description}>{event.description}</Text>
        <View style={styles.tags}>
          {event.tags.map((tag) => <View key={tag} style={styles.tag}><Text style={styles.tagText}>{tag}</Text></View>)}
        </View>

        <View style={styles.matchBox}>
          <View style={styles.matchTitleRow}>
            <Ionicons color={BrandColors.accentDark} name="bulb-outline" size={20} />
            <Text style={styles.matchTitle}>Neden sana önerdik?</Text>
          </View>
          {event.reasons.map((reason) => (
            <View key={reason} style={styles.reasonRow}>
              <Ionicons color={BrandColors.primary} name="checkmark-circle" size={17} />
              <Text style={styles.reasonText}>{reason}</Text>
            </View>
          ))}
        </View>

        <Pressable onPress={() => Alert.alert('İlgin kaydedildi', 'Etkinlik yaklaşınca sana hatırlatacağız.')} style={({ pressed }) => [styles.primaryButton, pressed && styles.pressed]}>
          <Text style={styles.primaryButtonText}>İlgileniyorum</Text>
          <Ionicons color={BrandColors.surface} name="arrow-forward" size={19} />
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}

function InfoItem({ icon, label, value }: { icon: keyof typeof Ionicons.glyphMap; label: string; value: string }) {
  return (
    <View style={styles.infoItem}>
      <Ionicons color={BrandColors.primary} name={icon} size={19} />
      <View style={styles.infoCopy}>
        <Text style={styles.infoLabel}>{label}</Text>
        <Text numberOfLines={1} style={styles.infoValue}>{value}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  safeArea: { backgroundColor: BrandColors.background, flex: 1 },
  content: { paddingBottom: 34, paddingHorizontal: 20, paddingTop: 10 },
  topBar: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 14 },
  iconButton: { alignItems: 'center', backgroundColor: BrandColors.surface, borderColor: BrandColors.border, borderRadius: 20, borderWidth: 1, height: 40, justifyContent: 'center', width: 40 },
  hero: { alignItems: 'center', borderRadius: 28, height: 230, justifyContent: 'center', position: 'relative' },
  scoreBadge: { alignItems: 'center', backgroundColor: 'rgba(255,255,255,0.88)', borderRadius: 999, bottom: 16, flexDirection: 'row', gap: 6, paddingHorizontal: 12, paddingVertical: 8, position: 'absolute' },
  scoreText: { color: BrandColors.primary, fontFamily: Fonts.rounded, fontSize: 12, fontWeight: '800' },
  club: { color: BrandColors.primary, fontFamily: Fonts.rounded, fontSize: 12, fontWeight: '800', letterSpacing: 0.5, marginTop: 22, textTransform: 'uppercase' },
  title: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 29, fontWeight: '800', lineHeight: 35, marginTop: 5 },
  infoGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginTop: 20 },
  infoItem: { alignItems: 'center', backgroundColor: BrandColors.surface, borderColor: BrandColors.border, borderRadius: 16, borderWidth: 1, flexDirection: 'row', padding: 12, width: '48%' },
  infoCopy: { flex: 1, marginLeft: 9 },
  infoLabel: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 10 },
  infoValue: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 13, fontWeight: '700', marginTop: 2 },
  sectionTitle: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 18, fontWeight: '800', marginTop: 25 },
  description: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 15, lineHeight: 23, marginTop: 8 },
  tags: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 15 },
  tag: { backgroundColor: BrandColors.primarySoft, borderRadius: 999, paddingHorizontal: 12, paddingVertical: 7 },
  tagText: { color: BrandColors.primary, fontFamily: Fonts.rounded, fontSize: 12, fontWeight: '700' },
  matchBox: { backgroundColor: BrandColors.accentSoft, borderColor: BrandColors.accentBorder, borderRadius: 20, borderWidth: 1, marginTop: 24, padding: 16 },
  matchTitleRow: { alignItems: 'center', flexDirection: 'row', gap: 8, marginBottom: 10 },
  matchTitle: { color: BrandColors.accentDark, fontFamily: Fonts.rounded, fontSize: 15, fontWeight: '800' },
  reasonRow: { alignItems: 'center', flexDirection: 'row', gap: 8, marginTop: 6 },
  reasonText: { color: BrandColors.text, flex: 1, fontFamily: Fonts.rounded, fontSize: 13, lineHeight: 18 },
  primaryButton: { alignItems: 'center', backgroundColor: BrandColors.primary, borderRadius: 17, flexDirection: 'row', gap: 8, justifyContent: 'center', marginTop: 24, minHeight: 54, paddingHorizontal: 20 },
  primaryButtonText: { color: BrandColors.surface, fontFamily: Fonts.rounded, fontSize: 16, fontWeight: '800' },
  pressed: { opacity: 0.88 },
  notFound: { flex: 1, justifyContent: 'center', padding: 24 },
});
