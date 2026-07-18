import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useEffect, useRef } from 'react';
import {
  Animated,
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { BrandColors, Fonts } from '@/constants/theme';

const benefits = [
  { icon: 'sparkles-outline' as const, label: 'Sana özel öneriler' },
  { icon: 'compass-outline' as const, label: 'Kolay keşif' },
  { icon: 'bulb-outline' as const, label: 'Açıklanabilir eşleşme' },
];

export default function OnboardingScreen() {
  const fade = useRef(new Animated.Value(0)).current;
  const rise = useRef(new Animated.Value(24)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fade, {
        toValue: 1,
        duration: 650,
        useNativeDriver: true,
      }),
      Animated.spring(rise, {
        toValue: 0,
        damping: 16,
        stiffness: 95,
        useNativeDriver: true,
      }),
    ]).start();
  }, [fade, rise]);

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.background}>
        <View style={styles.blobTop} />
        <View style={styles.blobBottom} />

        <Animated.View
          style={[
            styles.content,
            { opacity: fade, transform: [{ translateY: rise }] },
          ]}>
          <View style={styles.brandRow}>
            <View style={styles.logoMark}>
              <Ionicons name="leaf" size={22} color={BrandColors.primary} />
            </View>
            <Text style={styles.brandName}>CampusMatch</Text>
          </View>

          <View style={styles.heroArea}>
            <View style={styles.eventCardBack} />
            <View style={styles.eventCard}>
              <View style={styles.cardHeader}>
                <View style={styles.categoryIcon}>
                  <Ionicons name="code-slash" size={22} color={BrandColors.primary} />
                </View>
                <View style={styles.matchBadge}>
                  <Ionicons name="sparkles" size={13} color={BrandColors.primary} />
                  <Text style={styles.matchText}>%92 uyum</Text>
                </View>
              </View>

              <Text style={styles.cardEyebrow}>SANA ÖZEL SEÇİLDİ</Text>
              <Text style={styles.cardTitle}>Yapay Zeka Atölyesi</Text>
              <Text style={styles.cardMeta}>Teknoloji Kulübü · Cuma 18.00</Text>

              <View style={styles.reasonRow}>
                <Ionicons name="checkmark-circle" size={18} color={BrandColors.primary} />
                <Text style={styles.reasonText}>İlgi alanların ve başlangıç seviyenle eşleşiyor.</Text>
              </View>
            </View>

            <View style={styles.floatingClub}>
              <Ionicons name="people" size={18} color={BrandColors.accentDark} />
              <Text style={styles.floatingClubText}>Yeni topluluklar</Text>
            </View>
          </View>

          <View style={styles.copyArea}>
            <Text style={styles.title}>Kampüsünü kendine göre keşfet.</Text>
            <Text style={styles.subtitle}>
              İlgi alanlarını paylaş; sana uygun kulüp ve etkinlikleri tek yerde bul.
            </Text>
          </View>

          <View style={styles.benefitRow}>
            {benefits.map((benefit) => (
              <View key={benefit.label} style={styles.benefitItem}>
                <View style={styles.benefitIcon}>
                  <Ionicons name={benefit.icon} size={18} color={BrandColors.primary} />
                </View>
                <Text style={styles.benefitLabel}>{benefit.label}</Text>
              </View>
            ))}
          </View>

          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Keşfetmeye başla"
            onPress={() => router.push('/profile-setup')}
            style={({ pressed }) => [styles.primaryButton, pressed && styles.buttonPressed]}>
            <Text style={styles.primaryButtonText}>Keşfetmeye başla</Text>
            <View style={styles.buttonIcon}>
              <Ionicons name="arrow-forward" size={20} color={BrandColors.primary} />
            </View>
          </Pressable>

          <Text style={styles.footerText}>Doğru etkinlik, doğru zamanda.</Text>
        </Animated.View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: BrandColors.background,
  },
  background: {
    flex: 1,
    overflow: 'hidden',
    backgroundColor: BrandColors.background,
  },
  blobTop: {
    position: 'absolute',
    top: -120,
    right: -90,
    width: 270,
    height: 270,
    borderRadius: 140,
    backgroundColor: BrandColors.primarySoft,
    opacity: 0.72,
  },
  blobBottom: {
    position: 'absolute',
    bottom: -150,
    left: -100,
    width: 300,
    height: 300,
    borderRadius: 160,
    backgroundColor: BrandColors.accentSoft,
    opacity: 0.55,
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 14,
    paddingBottom: 12,
  },
  brandRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  logoMark: {
    width: 42,
    height: 42,
    borderRadius: 15,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: BrandColors.surface,
    borderWidth: 1,
    borderColor: BrandColors.border,
  },
  brandName: {
    fontFamily: Fonts?.rounded,
    fontSize: 21,
    fontWeight: '700',
    letterSpacing: -0.4,
    color: BrandColors.text,
  },
  heroArea: {
    flex: 1,
    minHeight: 270,
    justifyContent: 'center',
    paddingTop: 14,
  },
  eventCardBack: {
    position: 'absolute',
    left: 22,
    right: 5,
    top: '25%',
    height: 190,
    borderRadius: 30,
    backgroundColor: BrandColors.primarySoft,
    transform: [{ rotate: '5deg' }],
  },
  eventCard: {
    marginHorizontal: 8,
    padding: 22,
    borderRadius: 30,
    backgroundColor: BrandColors.surface,
    borderWidth: 1,
    borderColor: BrandColors.border,
    shadowColor: BrandColors.shadow,
    shadowOffset: { width: 0, height: 14 },
    shadowOpacity: 0.12,
    shadowRadius: 24,
    elevation: 5,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 22,
  },
  categoryIcon: {
    width: 46,
    height: 46,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: BrandColors.primarySoft,
  },
  matchBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
    paddingHorizontal: 11,
    paddingVertical: 7,
    borderRadius: 18,
    backgroundColor: BrandColors.background,
  },
  matchText: {
    fontSize: 12,
    fontWeight: '700',
    color: BrandColors.primary,
  },
  cardEyebrow: {
    marginBottom: 6,
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 1.2,
    color: BrandColors.primary,
  },
  cardTitle: {
    fontFamily: Fonts?.rounded,
    fontSize: 24,
    fontWeight: '700',
    letterSpacing: -0.5,
    color: BrandColors.text,
  },
  cardMeta: {
    marginTop: 6,
    fontSize: 13,
    color: BrandColors.textMuted,
  },
  reasonRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginTop: 18,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: BrandColors.border,
  },
  reasonText: {
    flex: 1,
    fontSize: 12,
    lineHeight: 17,
    color: BrandColors.textMuted,
  },
  floatingClub: {
    position: 'absolute',
    right: -2,
    bottom: 17,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 7,
    paddingHorizontal: 13,
    paddingVertical: 10,
    borderRadius: 18,
    backgroundColor: BrandColors.accentSoft,
    borderWidth: 1,
    borderColor: BrandColors.accentBorder,
  },
  floatingClubText: {
    fontSize: 11,
    fontWeight: '700',
    color: BrandColors.accentDark,
  },
  copyArea: {
    marginTop: 2,
  },
  title: {
    maxWidth: 330,
    fontFamily: Fonts?.rounded,
    fontSize: 34,
    lineHeight: 39,
    fontWeight: '700',
    letterSpacing: -1.1,
    color: BrandColors.text,
  },
  subtitle: {
    maxWidth: 340,
    marginTop: 11,
    fontSize: 15,
    lineHeight: 22,
    color: BrandColors.textMuted,
  },
  benefitRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 8,
    marginTop: 20,
    marginBottom: 22,
  },
  benefitItem: {
    flex: 1,
    alignItems: 'center',
    gap: 7,
  },
  benefitIcon: {
    width: 36,
    height: 36,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: BrandColors.primarySoft,
  },
  benefitLabel: {
    textAlign: 'center',
    fontSize: 10,
    lineHeight: 14,
    fontWeight: '600',
    color: BrandColors.textMuted,
  },
  primaryButton: {
    minHeight: 58,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingLeft: 22,
    paddingRight: 8,
    borderRadius: 21,
    backgroundColor: BrandColors.primary,
  },
  buttonPressed: {
    opacity: 0.88,
    transform: [{ scale: 0.99 }],
  },
  primaryButtonText: {
    fontSize: 16,
    fontWeight: '700',
    color: BrandColors.surface,
  },
  buttonIcon: {
    width: 44,
    height: 44,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: BrandColors.surface,
  },
  footerText: {
    marginTop: 10,
    textAlign: 'center',
    fontSize: 11,
    color: BrandColors.textMuted,
  },
});
