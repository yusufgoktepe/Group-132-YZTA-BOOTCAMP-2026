import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useMemo, useState } from 'react';
import {
  KeyboardAvoidingView,
  Alert,
  Platform,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { BrandColors, Fonts } from '@/constants/theme';
import { useApp } from '@/context/app-context';
import {
  EDUCATION_REFERENCE_VERSION,
  getClassYearOptions,
  universities,
} from '@/data/education';
import {
  feePreferences,
  interestGroups,
  languagePreferences,
  participationGoals,
  participationModes,
} from '@/data/profile-options';

type Option = { id: string; label: string };

function OptionChips({
  options,
  selected,
  onToggle,
  single = false,
}: {
  options: Option[];
  selected: string[];
  onToggle: (id: string) => void;
  single?: boolean;
}) {
  return (
    <View style={styles.chipGrid}>
      {options.map((option) => {
        const isSelected = selected.includes(option.id);
        return (
          <Pressable
            accessibilityRole={single ? 'radio' : 'checkbox'}
            accessibilityState={{ checked: isSelected }}
            key={option.id}
            onPress={() => onToggle(option.id)}
            style={[styles.chip, isSelected && styles.chipSelected]}>
            {isSelected && !single ? (
              <Ionicons color={BrandColors.surface} name="checkmark" size={15} />
            ) : null}
            <Text style={[styles.chipText, isSelected && styles.chipTextSelected]}>
              {option.label}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

export default function ProfileSetupScreen() {
  const { profile, saveProfile } = useApp();
  const [step, setStep] = useState(0);
  const [displayName, setDisplayName] = useState(profile?.displayName ?? '');
  const [universityQuery, setUniversityQuery] = useState(profile?.universityName ?? '');
  const [universityId, setUniversityId] = useState(profile?.universityId ?? '');
  const [programId, setProgramId] = useState(profile?.programId ?? '');
  const [classYear, setClassYear] = useState(profile?.classYear ?? '');
  const [interestIds, setInterestIds] = useState<string[]>(profile?.interestIds ?? []);
  const [goalIds, setGoalIds] = useState<string[]>(profile?.participationGoalIds ?? []);
  const [modeIds, setModeIds] = useState<string[]>(profile?.participationModes ?? []);
  const [feePreference, setFeePreference] = useState(profile?.feePreference ?? '');
  const [languagePreference, setLanguagePreference] = useState(profile?.languagePreference ?? '');

  const selectedUniversity = universities.find((item) => item.id === universityId);
  const selectedProgram = selectedUniversity?.programs.find((item) => item.id === programId);
  const classOptions = getClassYearOptions(selectedProgram).map((year) => ({
    id: year,
    label: year === 'prep' ? 'Hazırlık' : `${year}. sınıf`,
  }));
  const filteredUniversities = universities.filter((item) =>
    `${item.name} ${item.city}`.toLocaleLowerCase('tr-TR').includes(
      universityQuery.trim().toLocaleLowerCase('tr-TR')
    )
  );

  const titles = [
    ['Üniversiteni seç', 'Türkiye’deki üniversiteler arasından eğitim aldığın kurumu seç.'],
    ['Program ve sınıf', 'Programına göre yalnızca geçerli sınıf seçeneklerini gösteriyoruz.'],
    ['Neler ilgini çekiyor?', 'Sana uygun etkinlikler için 3–10 ilgi alanı seç.'],
    ['Etkinlik tercihlerin', 'Neden katıldığını ve temel tercihlerini belirle.'],
  ];

  const isCurrentStepValid = useMemo(() => {
    if (step === 0) return Boolean(universityId);
    if (step === 1) return Boolean(programId && classYear);
    if (step === 2) return interestIds.length >= 3 && interestIds.length <= 10;
    return Boolean(goalIds.length && modeIds.length && feePreference && languagePreference);
  }, [classYear, feePreference, goalIds.length, interestIds.length, languagePreference, modeIds.length, programId, step, universityId]);

  const toggleMulti = (id: string, selected: string[], setter: (value: string[]) => void, max?: number) => {
    if (selected.includes(id)) {
      setter(selected.filter((item) => item !== id));
      return;
    }
    if (!max || selected.length < max) setter([...selected, id]);
  };

  const selectUniversity = (id: string) => {
    const university = universities.find((item) => item.id === id);
    if (!university) return;
    setUniversityId(id);
    setUniversityQuery(university.name);
    setProgramId('');
    setClassYear('');
  };

  const handleBack = () => {
    if (step === 0) router.back();
    else setStep((current) => current - 1);
  };

  const handleContinue = () => {
    if (!isCurrentStepValid) return;
    if (step < 3) {
      setStep((current) => current + 1);
      return;
    }
    if (!selectedUniversity || !selectedProgram) return;

    saveProfile({
      schemaVersion: '2.0',
      educationReferenceVersion: EDUCATION_REFERENCE_VERSION,
      displayName: displayName.trim(),
      universityId: selectedUniversity.id,
      universityName: selectedUniversity.name,
      programId: selectedProgram.id,
      programName: selectedProgram.name,
      educationLevel: selectedProgram.level,
      programDuration: selectedProgram.duration,
      classYear,
      interestIds,
      participationGoalIds: goalIds,
      participationModes: modeIds,
      feePreference,
      languagePreference,
      campusId: null,
    });
    router.replace('/(tabs)');
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.keyboardView}>
        <View style={styles.header}>
          <Pressable accessibilityLabel="Geri" onPress={handleBack} style={styles.backButton}>
            <Ionicons color={BrandColors.text} name="arrow-back" size={21} />
          </Pressable>
          <View style={styles.progressTrack}>
            {[0, 1, 2, 3].map((item) => (
              <View key={item} style={[styles.progressSegment, item <= step && styles.progressSegmentActive]} />
            ))}
          </View>
          <Text style={styles.stepText}>{step + 1}/4</Text>
        </View>

        <ScrollView contentContainerStyle={styles.scrollContent} keyboardShouldPersistTaps="handled" showsVerticalScrollIndicator={false}>
          <View style={styles.titleArea}>
            <Text style={styles.eyebrow}>PROFİLİNİ OLUŞTUR</Text>
            <Text style={styles.title}>{titles[step][0]}</Text>
            <Text style={styles.subtitle}>{titles[step][1]}</Text>
          </View>

          {step === 0 ? (
            <View style={styles.formArea}>
              <View style={styles.fieldGroup}>
                <Text style={styles.label}>Görünmesini istediğin ad <Text style={styles.optional}>(isteğe bağlı)</Text></Text>
                <TextInput autoCapitalize="words" onChangeText={setDisplayName} placeholder="Örn. Deniz" placeholderTextColor={BrandColors.placeholder} style={styles.input} value={displayName} />
              </View>
              <View style={styles.fieldGroup}>
                <Text style={styles.label}>Üniversite ara</Text>
                <View style={styles.searchBox}>
                  <Ionicons color={BrandColors.textMuted} name="search" size={19} />
                  <TextInput onChangeText={(value) => { setUniversityQuery(value); if (value !== selectedUniversity?.name) setUniversityId(''); }} placeholder="Üniversite veya şehir" placeholderTextColor={BrandColors.placeholder} style={styles.searchInput} value={universityQuery} />
                </View>
                <View style={styles.selectList}>
                  {filteredUniversities.map((university) => {
                    const isSelected = university.id === universityId;
                    return (
                      <Pressable key={university.id} onPress={() => selectUniversity(university.id)} style={[styles.selectCard, isSelected && styles.selectCardActive]}>
                        <View style={styles.selectIcon}><Ionicons color={BrandColors.primary} name="school-outline" size={20} /></View>
                        <View style={styles.selectCopy}><Text style={styles.selectTitle}>{university.name}</Text><Text style={styles.selectMeta}>{university.city} · {university.type === 'state' ? 'Devlet' : 'Vakıf'}</Text></View>
                        {isSelected ? <Ionicons color={BrandColors.primary} name="checkmark-circle" size={22} /> : null}
                      </Pressable>
                    );
                  })}
                </View>
                <Pressable
                  onPress={() =>
                    Alert.alert(
                      'Üniversiten listede yok mu?',
                      'Liste şu anda geliştirme verisi kullanıyor. Tam YÖK referansı eklendiğinde Türkiye’deki aktif üniversiteler burada yer alacak.'
                    )
                  }
                  style={styles.missingButton}>
                  <Ionicons color={BrandColors.textMuted} name="help-circle-outline" size={18} />
                  <Text style={styles.missingText}>Üniversitemi bulamıyorum</Text>
                </Pressable>
              </View>
            </View>
          ) : null}

          {step === 1 ? (
            <View style={styles.formArea}>
              <View style={styles.selectedSchool}><Ionicons color={BrandColors.primary} name="school" size={20} /><Text style={styles.selectedSchoolText}>{selectedUniversity?.name}</Text></View>
              <View style={styles.fieldGroup}>
                <Text style={styles.label}>Programın</Text>
                <View style={styles.selectList}>
                  {selectedUniversity?.programs.map((program) => {
                    const isSelected = program.id === programId;
                    return (
                      <Pressable key={program.id} onPress={() => { setProgramId(program.id); setClassYear(''); }} style={[styles.selectCard, isSelected && styles.selectCardActive]}>
                        <View style={styles.selectCopy}><Text style={styles.selectTitle}>{program.name}</Text><Text style={styles.selectMeta}>{program.duration} yıl · {program.level === 'associate' ? 'Ön lisans' : 'Lisans'}</Text></View>
                        {isSelected ? <Ionicons color={BrandColors.primary} name="checkmark-circle" size={22} /> : null}
                      </Pressable>
                    );
                  })}
                </View>
              </View>
              {selectedProgram ? <View style={styles.fieldGroup}><Text style={styles.label}>Sınıfın</Text><OptionChips onToggle={setClassYear} options={classOptions} selected={classYear ? [classYear] : []} single /></View> : null}
            </View>
          ) : null}

          {step === 2 ? (
            <View style={styles.formArea}>
              <View style={styles.selectionBanner}><Text style={styles.selectionBannerText}>{interestIds.length}/10 seçildi</Text><Text style={styles.selectionHint}>En az 3 seçim gerekli</Text></View>
              {interestGroups.map((group) => (
                <View key={group.title} style={styles.fieldGroup}><Text style={styles.groupTitle}>{group.title}</Text><OptionChips onToggle={(id) => toggleMulti(id, interestIds, setInterestIds, 10)} options={group.options} selected={interestIds} /></View>
              ))}
            </View>
          ) : null}

          {step === 3 ? (
            <View style={styles.formArea}>
              <View style={styles.fieldGroup}><Text style={styles.label}>Etkinliklere neden katılmak istiyorsun?</Text><OptionChips onToggle={(id) => toggleMulti(id, goalIds, setGoalIds)} options={participationGoals} selected={goalIds} /></View>
              <View style={styles.fieldGroup}><Text style={styles.label}>Katılım biçimi</Text><OptionChips onToggle={(id) => toggleMulti(id, modeIds, setModeIds)} options={participationModes} selected={modeIds} /></View>
              <View style={styles.fieldGroup}><Text style={styles.label}>Ücret tercihi</Text><OptionChips onToggle={setFeePreference} options={feePreferences} selected={feePreference ? [feePreference] : []} single /></View>
              <View style={styles.fieldGroup}><Text style={styles.label}>Etkinlik dili</Text><OptionChips onToggle={setLanguagePreference} options={languagePreferences} selected={languagePreference ? [languagePreference] : []} single /></View>
            </View>
          ) : null}
        </ScrollView>

        <View style={styles.footer}>
          <Pressable disabled={!isCurrentStepValid} onPress={handleContinue} style={({ pressed }) => [styles.continueButton, !isCurrentStepValid && styles.continueButtonDisabled, pressed && isCurrentStepValid && styles.continueButtonPressed]}>
            <Text style={styles.continueButtonText}>{step === 3 ? 'Profilimi tamamla' : 'Devam et'}</Text>
            <Ionicons color={BrandColors.surface} name={step === 3 ? 'checkmark' : 'arrow-forward'} size={20} />
          </Pressable>
          <Text style={styles.privacyText}>Bilgilerin yalnızca önerilerini kişiselleştirmek için kullanılır.</Text>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { backgroundColor: BrandColors.background, flex: 1 },
  keyboardView: { flex: 1 },
  header: { alignItems: 'center', flexDirection: 'row', gap: 14, paddingBottom: 10, paddingHorizontal: 20, paddingTop: 10 },
  backButton: { alignItems: 'center', backgroundColor: BrandColors.surface, borderColor: BrandColors.border, borderRadius: 15, borderWidth: 1, height: 42, justifyContent: 'center', width: 42 },
  progressTrack: { flex: 1, flexDirection: 'row', gap: 6 },
  progressSegment: { backgroundColor: BrandColors.border, borderRadius: 4, flex: 1, height: 5 },
  progressSegmentActive: { backgroundColor: BrandColors.primary },
  stepText: { color: BrandColors.textMuted, fontSize: 12, fontWeight: '700', minWidth: 28 },
  scrollContent: { paddingBottom: 30, paddingHorizontal: 24, paddingTop: 20 },
  titleArea: { marginBottom: 26 },
  eyebrow: { color: BrandColors.primary, fontSize: 10, fontWeight: '800', letterSpacing: 1.35, marginBottom: 8 },
  title: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 31, fontWeight: '800', letterSpacing: -0.8, lineHeight: 37 },
  subtitle: { color: BrandColors.textMuted, fontSize: 14, lineHeight: 21, marginTop: 9, maxWidth: 360 },
  formArea: { gap: 23 },
  fieldGroup: { gap: 10 },
  label: { color: BrandColors.text, fontSize: 13, fontWeight: '700' },
  optional: { color: BrandColors.textMuted, fontWeight: '500' },
  input: { backgroundColor: BrandColors.surface, borderColor: BrandColors.border, borderRadius: 18, borderWidth: 1, color: BrandColors.text, fontSize: 15, minHeight: 54, paddingHorizontal: 16 },
  searchBox: { alignItems: 'center', backgroundColor: BrandColors.surface, borderColor: BrandColors.border, borderRadius: 18, borderWidth: 1, flexDirection: 'row', gap: 9, minHeight: 54, paddingHorizontal: 15 },
  searchInput: { color: BrandColors.text, flex: 1, fontSize: 15, minHeight: 52 },
  selectList: { gap: 9 },
  selectCard: { alignItems: 'center', backgroundColor: BrandColors.surface, borderColor: BrandColors.border, borderRadius: 17, borderWidth: 1, flexDirection: 'row', minHeight: 66, padding: 13 },
  selectCardActive: { backgroundColor: BrandColors.primarySoft, borderColor: BrandColors.primary },
  selectIcon: { alignItems: 'center', backgroundColor: BrandColors.primarySoft, borderRadius: 13, height: 40, justifyContent: 'center', marginRight: 11, width: 40 },
  selectCopy: { flex: 1 },
  selectTitle: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 14, fontWeight: '700' },
  selectMeta: { color: BrandColors.textMuted, fontSize: 12, marginTop: 4 },
  missingButton: { alignItems: 'center', flexDirection: 'row', gap: 6, justifyContent: 'center', padding: 8 },
  missingText: { color: BrandColors.textMuted, fontSize: 12, fontWeight: '600' },
  selectedSchool: { alignItems: 'center', backgroundColor: BrandColors.primarySoft, borderRadius: 16, flexDirection: 'row', gap: 9, padding: 14 },
  selectedSchoolText: { color: BrandColors.primary, flex: 1, fontSize: 13, fontWeight: '700' },
  chipGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 9 },
  chip: { alignItems: 'center', backgroundColor: BrandColors.surface, borderColor: BrandColors.border, borderRadius: 16, borderWidth: 1, flexDirection: 'row', gap: 5, minHeight: 42, paddingHorizontal: 14, paddingVertical: 10 },
  chipSelected: { backgroundColor: BrandColors.primary, borderColor: BrandColors.primary },
  chipText: { color: BrandColors.textMuted, fontSize: 13, fontWeight: '600' },
  chipTextSelected: { color: BrandColors.surface },
  groupTitle: { color: BrandColors.text, fontFamily: Fonts.rounded, fontSize: 15, fontWeight: '800' },
  selectionBanner: { alignItems: 'center', backgroundColor: BrandColors.primarySoft, borderRadius: 15, flexDirection: 'row', justifyContent: 'space-between', padding: 13 },
  selectionBannerText: { color: BrandColors.primary, fontSize: 13, fontWeight: '800' },
  selectionHint: { color: BrandColors.textMuted, fontSize: 11 },
  footer: { backgroundColor: BrandColors.background, borderTopColor: BrandColors.border, borderTopWidth: 1, paddingBottom: Platform.OS === 'ios' ? 8 : 16, paddingHorizontal: 24, paddingTop: 12 },
  continueButton: { alignItems: 'center', backgroundColor: BrandColors.primary, borderRadius: 20, flexDirection: 'row', gap: 10, justifyContent: 'center', minHeight: 56 },
  continueButtonDisabled: { backgroundColor: BrandColors.disabled },
  continueButtonPressed: { opacity: 0.88, transform: [{ scale: 0.99 }] },
  continueButtonText: { color: BrandColors.surface, fontSize: 15, fontWeight: '700' },
  privacyText: { color: BrandColors.textMuted, fontSize: 10, marginTop: 9, textAlign: 'center' },
});
