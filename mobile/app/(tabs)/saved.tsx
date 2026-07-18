import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';

import { EventCard } from '@/components/event-card';
import { BrandColors, Fonts } from '@/constants/theme';
import { useApp } from '@/context/app-context';
import { events } from '@/mocks/events';

export default function SavedEventsScreen() {
  const { savedEventIds, toggleSavedEvent } = useApp();
  const savedEvents = events.filter((event) => savedEventIds.includes(event.id));

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <Text style={styles.eyebrow}>KOLEKSİYONUN</Text>
        <Text style={styles.title}>Kaydedilenler</Text>
        <Text style={styles.subtitle}>Daha sonra incelemek istediğin etkinlikler burada.</Text>
        {savedEvents.length > 0 ? (
          <View style={styles.list}>
            {savedEvents.map((event) => (
              <EventCard
                event={event}
                isSaved
                key={event.id}
                onPress={() => router.push({ pathname: '/event/[id]', params: { id: event.id } })}
                onToggleSaved={() => toggleSavedEvent(event.id)}
              />
            ))}
          </View>
        ) : (
          <View style={styles.emptyState}>
            <View style={styles.emptyIcon}><Ionicons color={BrandColors.primary} name="bookmark-outline" size={32} /></View>
            <Text style={styles.emptyTitle}>Henüz etkinlik kaydetmedin</Text>
            <Text style={styles.emptyText}>Keşfet ekranındaki yer imi simgesine dokunarak başlayabilirsin.</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { backgroundColor: BrandColors.background, flex: 1 },
  content: { flexGrow: 1, paddingBottom: 30, paddingHorizontal: 20, paddingTop: 16 },
  eyebrow: { color: BrandColors.primary, fontFamily: Fonts.rounded, fontSize: 11, fontWeight: '800', letterSpacing: 1.5 },
  title: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 30, fontWeight: '800', marginTop: 4 },
  subtitle: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 14, lineHeight: 20, marginTop: 6 },
  list: { marginTop: 24 },
  emptyState: { alignItems: 'center', flex: 1, justifyContent: 'center', paddingBottom: 80, paddingHorizontal: 25 },
  emptyIcon: { alignItems: 'center', backgroundColor: BrandColors.primarySoft, borderRadius: 30, height: 60, justifyContent: 'center', marginBottom: 18, width: 60 },
  emptyTitle: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 18, fontWeight: '800', textAlign: 'center' },
  emptyText: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 14, lineHeight: 21, marginTop: 7, textAlign: 'center' },
});
