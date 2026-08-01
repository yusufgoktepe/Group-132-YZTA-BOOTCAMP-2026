import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { ActivityIndicator, Alert, Pressable, SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';

import { BrandColors, Fonts } from '@/constants/theme';
import { useApp } from '@/context/app-context';
import { fetchParticipations, rateEvent, type Participation } from '@/services/events-api';

const STATUS_LABELS: Record<Participation['status'], string> = {
  requested: 'İstek gönderildi', approved: 'Onaylandı', rejected: 'Reddedildi',
  cancelled: 'İptal edildi', attended: 'Katılım doğrulandı', no_show: 'Katılmadı',
};

export default function ParticipationsScreen() {
  const { profileId } = useApp();
  const [items, setItems] = useState<Participation[]>([]);
  const [loading, setLoading] = useState(true);
  const [ratedIds, setRatedIds] = useState<string[]>([]);

  const load = useCallback(async () => {
    if (!profileId) { setLoading(false); return; }
    setLoading(true);
    try {
      const payload = await fetchParticipations(profileId);
      setItems(payload?.participations ?? []);
    } catch (error) {
      Alert.alert('Katılımlar alınamadı', error instanceof Error ? error.message : 'Bilinmeyen hata');
    } finally { setLoading(false); }
  }, [profileId]);

  useFocusEffect(useCallback(() => { void load(); }, [load]));

  const submitRating = async (item: Participation, score: number) => {
    if (!profileId) return;
    try {
      await rateEvent(item.event_id, profileId, score);
      setRatedIds((current) => [...current, item.participation_id]);
      Alert.alert('Teşekkürler', 'Puanın anonim olarak organizatör güven skoruna eklendi.');
    } catch (error) {
      Alert.alert('Puan kaydedilemedi', error instanceof Error ? error.message : 'Bilinmeyen hata');
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.eyebrow}>ETKİNLİK GEÇMİŞİ</Text>
        <Text style={styles.title}>Katılımlarım</Text>
        <Text style={styles.subtitle}>Katılımın organizatör tarafından doğrulandıktan sonra anonim puan verebilirsin.</Text>
        {loading ? <ActivityIndicator color={BrandColors.primary} size="large" style={styles.loader} /> : null}
        {!loading && !items.length ? <View style={styles.empty}><Ionicons color={BrandColors.primary} name="ticket-outline" size={34} /><Text style={styles.emptyTitle}>Henüz katılım isteğin yok</Text></View> : null}
        {items.map((item) => {
          const canRate = item.status === 'attended' && item.attendance_verified === 1 && item.has_rated !== 1 && !ratedIds.includes(item.participation_id);
          return <View key={item.participation_id} style={styles.card}>
            <View style={styles.cardTop}><Text style={styles.cardTitle}>{item.title}</Text><View style={styles.status}><Text style={styles.statusText}>{STATUS_LABELS[item.status]}</Text></View></View>
            <Text style={styles.meta}>{new Date(item.starts_at).toLocaleString('tr-TR')}</Text>
            {item.location_name ? <Text style={styles.meta}>{item.location_name}</Text> : null}
            {canRate ? <View style={styles.ratingBox}><Text style={styles.ratingTitle}>Organizatörü anonim puanla</Text><View style={styles.stars}>{[1, 2, 3, 4, 5].map((score) => <Pressable accessibilityLabel={`${score} yıldız ver`} accessibilityRole="button" key={score} onPress={() => void submitRating(item, score)}><Ionicons color="#E0A126" name="star" size={29} /></Pressable>)}</View></View> : null}
            {item.has_rated === 1 || ratedIds.includes(item.participation_id) ? <Text style={styles.rated}>✓ Puanın anonim olarak kaydedildi.</Text> : null}
          </View>;
        })}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { backgroundColor: BrandColors.background, flex: 1 }, content: { paddingBottom: 120, paddingHorizontal: 20, paddingTop: 20 },
  eyebrow: { color: BrandColors.primary, fontFamily: Fonts.rounded, fontSize: 11, fontWeight: '800', letterSpacing: 1.4 }, title: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 28, fontWeight: '800', marginTop: 5 },
  subtitle: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 14, lineHeight: 21, marginBottom: 16, marginTop: 7 }, loader: { marginTop: 70 },
  empty: { alignItems: 'center', backgroundColor: BrandColors.surface, borderRadius: 20, marginTop: 30, padding: 28 }, emptyTitle: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 16, fontWeight: '800', marginTop: 10 },
  card: { backgroundColor: BrandColors.surface, borderColor: BrandColors.border, borderRadius: 19, borderWidth: 1, marginTop: 12, padding: 16 }, cardTop: { alignItems: 'flex-start', flexDirection: 'row', gap: 8 }, cardTitle: { color: BrandColors.text, flex: 1, fontFamily: Fonts.rounded, fontSize: 16, fontWeight: '800' },
  status: { backgroundColor: BrandColors.primarySoft, borderRadius: 999, paddingHorizontal: 9, paddingVertical: 5 }, statusText: { color: BrandColors.primary, fontFamily: Fonts.rounded, fontSize: 10, fontWeight: '800' }, meta: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 12, marginTop: 6 },
  ratingBox: { borderTopColor: BrandColors.border, borderTopWidth: 1, marginTop: 14, paddingTop: 13 }, ratingTitle: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 13, fontWeight: '800' }, stars: { flexDirection: 'row', gap: 10, marginTop: 9 }, rated: { color: BrandColors.primary, fontFamily: Fonts.rounded, fontSize: 12, fontWeight: '700', marginTop: 13 },
});
