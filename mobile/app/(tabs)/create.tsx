import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useMemo, useState } from 'react';
import { ActivityIndicator, Alert, KeyboardAvoidingView, Platform, Pressable, SafeAreaView, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';

import { BrandColors, Fonts } from '@/constants/theme';
import { useApp } from '@/context/app-context';
import { createMicroEvent } from '@/services/events-api';
import { mapApiEvent } from '@/utils/api-event';

const MODES = [
  { id: 'onsite', label: 'Yüz yüze' },
  { id: 'online', label: 'Online' },
  { id: 'hybrid', label: 'Hibrit' },
] as const;

function futureIso(hours: number) {
  return new Date(Date.now() + hours * 60 * 60 * 1000).toISOString();
}

export default function CreateEventScreen() {
  const { profileId, registerFeedEvents } = useApp();
  const defaults = useMemo(() => ({ start: futureIso(24), end: futureIso(26), expiry: futureIso(27) }), []);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('community');
  const [interests, setInterests] = useState('social-community');
  const [location, setLocation] = useState('');
  const [quota, setQuota] = useState('10');
  const [startsAt, setStartsAt] = useState(defaults.start);
  const [endsAt, setEndsAt] = useState(defaults.end);
  const [expiresAt, setExpiresAt] = useState(defaults.expiry);
  const [mode, setMode] = useState<'onsite' | 'online' | 'hybrid'>('onsite');
  const [submitting, setSubmitting] = useState(false);

  const submit = async () => {
    if (!profileId) {
      Alert.alert('Profil gerekli', 'Mikro etkinlik oluşturmak için önce profilini tamamla.');
      return;
    }
    if (!title.trim() || description.trim().length < 10 || !location.trim()) {
      Alert.alert('Eksik bilgi', 'Başlık, en az 10 karakterlik açıklama ve konum zorunludur.');
      return;
    }
    setSubmitting(true);
    try {
      const raw = await createMicroEvent({
        creatorProfileId: profileId,
        title: title.trim(),
        description: description.trim(),
        categoryId: category.trim(),
        interestIds: interests.split(',').map((item) => item.trim()).filter(Boolean),
        targetGoalIds: ['socialize'],
        startsAt,
        endsAt,
        expiresAt,
        participationMode: mode,
        locationName: location.trim(),
        quota: Number(quota),
        language: 'tr',
      });
      const event = mapApiEvent(raw);
      registerFeedEvents([event]);
      Alert.alert('Etkinlik yayınlandı', 'Mikro etkinliğin kart kuyruğuna katılmaya hazır.', [
        { text: 'Detayı aç', onPress: () => router.push({ pathname: '/event/[id]', params: { id: event.id } }) },
      ]);
      setTitle('');
      setDescription('');
      setLocation('');
    } catch (error) {
      Alert.alert('Etkinlik oluşturulamadı', error instanceof Error ? error.message : 'Bilinmeyen bir hata oluştu.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.flex}>
        <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
          <Text style={styles.eyebrow}>MİKRO ETKİNLİK</Text>
          <Text style={styles.title}>Kampüste bir buluşma başlat</Text>
          <Text style={styles.subtitle}>Kısa ömürlü öğrenci aktiviteleri doğrudan yayınlanır ve süre dolunca feed’den çıkar.</Text>

          <Field label="Başlık" value={title} onChangeText={setTitle} placeholder="Örn. Masa oyunu buluşması" />
          <Field label="Açıklama" value={description} onChangeText={setDescription} placeholder="Etkinliğin amacını ve planını anlat" multiline />
          <Field label="Kategori" value={category} onChangeText={setCategory} placeholder="community" />
          <Field label="İlgi etiketleri" value={interests} onChangeText={setInterests} placeholder="board-games, social-community" hint="Birden fazlaysa virgülle ayır." />

          <Text style={styles.label}>Katılım biçimi</Text>
          <View style={styles.modeRow}>{MODES.map((item) => (
            <Pressable accessibilityRole="radio" accessibilityState={{ checked: mode === item.id }} key={item.id} onPress={() => setMode(item.id)} style={[styles.modeButton, mode === item.id && styles.modeButtonActive]}>
              <Text style={[styles.modeText, mode === item.id && styles.modeTextActive]}>{item.label}</Text>
            </Pressable>
          ))}</View>

          <Field label="Konum" value={location} onChangeText={setLocation} placeholder="Kampüs ve buluşma noktası" />
          <Field label="Kota" value={quota} onChangeText={setQuota} placeholder="10" keyboardType="number-pad" />
          <Field label="Başlangıç (ISO-8601)" value={startsAt} onChangeText={setStartsAt} />
          <Field label="Bitiş (ISO-8601)" value={endsAt} onChangeText={setEndsAt} />
          <Field label="İlanın sona ermesi (ISO-8601)" value={expiresAt} onChangeText={setExpiresAt} />

          <Pressable accessibilityRole="button" accessibilityState={{ busy: submitting, disabled: submitting }} disabled={submitting} onPress={submit} style={({ pressed }) => [styles.submit, (pressed || submitting) && styles.pressed]}>
            {submitting ? <ActivityIndicator color={BrandColors.surface} /> : <Ionicons color={BrandColors.surface} name="paper-plane-outline" size={19} />}
            <Text style={styles.submitText}>{submitting ? 'Yayınlanıyor…' : 'Etkinliği yayınla'}</Text>
          </Pressable>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

function Field({ label, hint, multiline, ...props }: { label: string; hint?: string; multiline?: boolean } & React.ComponentProps<typeof TextInput>) {
  return <View style={styles.field}><Text style={styles.label}>{label}</Text><TextInput accessibilityLabel={label} multiline={multiline} placeholderTextColor={BrandColors.placeholder} style={[styles.input, multiline && styles.multiline]} {...props} />{hint ? <Text style={styles.hint}>{hint}</Text> : null}</View>;
}

const styles = StyleSheet.create({
  safeArea: { backgroundColor: BrandColors.background, flex: 1 }, flex: { flex: 1 }, content: { paddingBottom: 120, paddingHorizontal: 20, paddingTop: 20 },
  eyebrow: { color: BrandColors.primary, fontFamily: Fonts.rounded, fontSize: 11, fontWeight: '800', letterSpacing: 1.4 },
  title: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 27, fontWeight: '800', marginTop: 5 },
  subtitle: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 14, lineHeight: 21, marginBottom: 12, marginTop: 8 },
  field: { marginTop: 15 }, label: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 13, fontWeight: '800', marginBottom: 7, marginTop: 14 },
  input: { backgroundColor: BrandColors.surface, borderColor: BrandColors.border, borderRadius: 15, borderWidth: 1, color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 14, minHeight: 49, paddingHorizontal: 14, paddingVertical: 12 },
  multiline: { minHeight: 100, textAlignVertical: 'top' }, hint: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 11, marginTop: 5 },
  modeRow: { flexDirection: 'row', gap: 8 }, modeButton: { backgroundColor: BrandColors.surface, borderColor: BrandColors.border, borderRadius: 12, borderWidth: 1, flex: 1, paddingVertical: 11 },
  modeButtonActive: { backgroundColor: BrandColors.primarySoft, borderColor: BrandColors.primary }, modeText: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 12, fontWeight: '700', textAlign: 'center' }, modeTextActive: { color: BrandColors.primary },
  submit: { alignItems: 'center', backgroundColor: BrandColors.primary, borderRadius: 17, flexDirection: 'row', gap: 8, justifyContent: 'center', marginTop: 26, minHeight: 55 }, submitText: { color: BrandColors.surface, fontFamily: Fonts.rounded, fontSize: 15, fontWeight: '800' }, pressed: { opacity: 0.8 },
});
