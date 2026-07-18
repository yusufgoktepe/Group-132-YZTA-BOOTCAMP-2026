import { Ionicons } from '@expo/vector-icons';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { BrandColors, Fonts } from '@/constants/theme';
import { CampusEvent } from '@/types/event';

type EventCardProps = {
  event: CampusEvent;
  isSaved: boolean;
  onPress: () => void;
  onToggleSaved: () => void;
};

export function EventCard({ event, isSaved, onPress, onToggleSaved }: EventCardProps) {
  return (
    <Pressable onPress={onPress} style={({ pressed }) => [styles.card, pressed && styles.pressed]}>
      <View style={[styles.visual, { backgroundColor: event.color }]}>
        <View style={styles.scoreBadge}>
          <Ionicons color={BrandColors.primary} name="sparkles" size={13} />
          <Text style={styles.scoreText}>%{event.matchScore} eşleşme</Text>
        </View>
        <Ionicons color={BrandColors.primary} name={event.icon} size={52} />
        <Pressable
          accessibilityLabel={isSaved ? 'Etkinliği kaydedilenlerden çıkar' : 'Etkinliği kaydet'}
          hitSlop={8}
          onPress={(pressEvent) => {
            pressEvent.stopPropagation();
            onToggleSaved();
          }}
          style={styles.saveButton}>
          <Ionicons
            color={isSaved ? BrandColors.primary : BrandColors.textMuted}
            name={isSaved ? 'bookmark' : 'bookmark-outline'}
            size={20}
          />
        </Pressable>
      </View>
      <View style={styles.content}>
        <Text style={styles.club}>{event.clubName}</Text>
        <Text numberOfLines={2} style={styles.title}>{event.title}</Text>
        <View style={styles.metaRow}>
          <Ionicons color={BrandColors.textMuted} name="calendar-outline" size={15} />
          <Text style={styles.metaText}>{event.dateLabel}</Text>
          <View style={styles.dot} />
          <Text style={styles.metaText}>{event.time}</Text>
        </View>
        <View style={styles.reason}>
          <Ionicons color={BrandColors.accentDark} name="bulb-outline" size={15} />
          <Text numberOfLines={1} style={styles.reasonText}>{event.reasons[0]}</Text>
        </View>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: BrandColors.surface, borderColor: BrandColors.border, borderRadius: 24, borderWidth: 1, marginBottom: 16, overflow: 'hidden', shadowColor: BrandColors.shadow, shadowOffset: { width: 0, height: 8 }, shadowOpacity: 0.08, shadowRadius: 18 },
  pressed: { opacity: 0.92, transform: [{ scale: 0.99 }] },
  visual: { alignItems: 'center', height: 132, justifyContent: 'center', position: 'relative' },
  scoreBadge: { alignItems: 'center', backgroundColor: 'rgba(255,255,255,0.84)', borderRadius: 999, flexDirection: 'row', gap: 5, left: 14, paddingHorizontal: 10, paddingVertical: 7, position: 'absolute', top: 14 },
  scoreText: { color: BrandColors.primary, fontFamily: Fonts.rounded, fontSize: 12, fontWeight: '700' },
  saveButton: { alignItems: 'center', backgroundColor: 'rgba(255,255,255,0.9)', borderRadius: 18, height: 36, justifyContent: 'center', position: 'absolute', right: 14, top: 14, width: 36 },
  content: { padding: 17 },
  club: { color: BrandColors.primary, fontFamily: Fonts.rounded, fontSize: 12, fontWeight: '700', letterSpacing: 0.3, marginBottom: 5, textTransform: 'uppercase' },
  title: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 20, fontWeight: '800', lineHeight: 25 },
  metaRow: { alignItems: 'center', flexDirection: 'row', marginTop: 10 },
  metaText: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 13, marginLeft: 5 },
  dot: { backgroundColor: BrandColors.border, borderRadius: 2, height: 4, marginHorizontal: 8, width: 4 },
  reason: { alignItems: 'center', backgroundColor: BrandColors.accentSoft, borderRadius: 12, flexDirection: 'row', gap: 7, marginTop: 13, paddingHorizontal: 10, paddingVertical: 9 },
  reasonText: { color: BrandColors.accentDark, flex: 1, fontFamily: Fonts.rounded, fontSize: 12, fontWeight: '600' },
});
