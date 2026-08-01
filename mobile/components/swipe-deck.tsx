import { Ionicons } from '@expo/vector-icons';
import { useEffect, useMemo, useRef } from 'react';
import { Animated, Dimensions, PanResponder, Pressable, StyleSheet, Text, View } from 'react-native';

import { EventCard } from '@/components/event-card';
import { BrandColors, Fonts } from '@/constants/theme';
import type { CampusEvent } from '@/types/event';

const SWIPE_THRESHOLD = 105;
const SCREEN_WIDTH = Dimensions.get('window').width;

type SwipeDeckProps = {
  event: CampusEvent;
  nextEvent?: CampusEvent;
  isSaved: boolean;
  onDetail: () => void;
  onLike: () => void;
  onSkip: () => void;
  onSave: () => void;
};

export function SwipeDeck({ event, nextEvent, isSaved, onDetail, onLike, onSkip, onSave }: SwipeDeckProps) {
  const position = useRef(new Animated.ValueXY()).current;
  const locked = useRef(false);

  useEffect(() => {
    position.setValue({ x: 0, y: 0 });
    locked.current = false;
  }, [event.id, position]);

  const completeSwipe = (direction: 'left' | 'right') => {
    if (locked.current) return;
    locked.current = true;
    Animated.timing(position, {
      toValue: { x: direction === 'right' ? SCREEN_WIDTH * 1.25 : -SCREEN_WIDTH * 1.25, y: 20 },
      duration: 230,
      useNativeDriver: true,
    }).start(() => (direction === 'right' ? onLike() : onSkip()));
  };

  const panResponder = useMemo(
    () =>
      PanResponder.create({
        onMoveShouldSetPanResponder: (_, gesture) => Math.abs(gesture.dx) > 8,
        onPanResponderMove: Animated.event([null, { dx: position.x, dy: position.y }], {
          useNativeDriver: false,
        }),
        onPanResponderRelease: (_, gesture) => {
          if (gesture.dx > SWIPE_THRESHOLD) completeSwipe('right');
          else if (gesture.dx < -SWIPE_THRESHOLD) completeSwipe('left');
          else {
            Animated.spring(position, {
              toValue: { x: 0, y: 0 },
              friction: 6,
              tension: 55,
              useNativeDriver: true,
            }).start();
          }
        },
        onPanResponderTerminate: () => {
          Animated.spring(position, {
            toValue: { x: 0, y: 0 },
            useNativeDriver: true,
          }).start();
        },
      }),
    // Callbacks always target the currently rendered event; event id recreates the responder.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [event.id, position]
  );

  const rotate = position.x.interpolate({
    inputRange: [-SCREEN_WIDTH, 0, SCREEN_WIDTH],
    outputRange: ['-13deg', '0deg', '13deg'],
    extrapolate: 'clamp',
  });
  const likeOpacity = position.x.interpolate({
    inputRange: [20, SWIPE_THRESHOLD],
    outputRange: [0, 1],
    extrapolate: 'clamp',
  });
  const skipOpacity = position.x.interpolate({
    inputRange: [-SWIPE_THRESHOLD, -20],
    outputRange: [1, 0],
    extrapolate: 'clamp',
  });

  return (
    <View style={styles.wrapper}>
      {nextEvent ? (
        <View pointerEvents="none" style={styles.nextCard}>
          <EventCard event={nextEvent} isSaved={false} onPress={() => undefined} onToggleSaved={() => undefined} />
        </View>
      ) : null}
      <Animated.View
        {...panResponder.panHandlers}
        style={[styles.card, { transform: [...position.getTranslateTransform(), { rotate }] }]}>
        <Animated.View pointerEvents="none" style={[styles.stamp, styles.likeStamp, { opacity: likeOpacity }]}>
          <Text style={styles.likeText}>İLGİLENİYORUM</Text>
        </Animated.View>
        <Animated.View pointerEvents="none" style={[styles.stamp, styles.skipStamp, { opacity: skipOpacity }]}>
          <Text style={styles.skipText}>GEÇ</Text>
        </Animated.View>
        <EventCard event={event} isSaved={isSaved} onPress={onDetail} onToggleSaved={onSave} />
      </Animated.View>

      <View style={styles.actions}>
        <Pressable accessibilityLabel="Etkinliği geç" accessibilityRole="button" onPress={() => completeSwipe('left')} style={[styles.action, styles.skipAction]}>
          <Ionicons color="#A94C4C" name="close" size={29} />
        </Pressable>
        <Pressable accessibilityLabel="Etkinliği kaydet" accessibilityRole="button" accessibilityState={{ selected: isSaved }} onPress={onSave} style={[styles.action, styles.saveAction]}>
          <Ionicons color={BrandColors.accentDark} name={isSaved ? 'bookmark' : 'bookmark-outline'} size={24} />
        </Pressable>
        <Pressable accessibilityLabel="Etkinlikle ilgileniyorum" accessibilityRole="button" onPress={() => completeSwipe('right')} style={[styles.action, styles.likeAction]}>
          <Ionicons color={BrandColors.primary} name="heart" size={27} />
        </Pressable>
      </View>
      <Text style={styles.hint}>Geçmek için sola · Beğenmek için sağa kaydır</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { flex: 1, justifyContent: 'center', minHeight: 520 },
  card: { zIndex: 2 },
  nextCard: { left: 8, opacity: 0.48, position: 'absolute', right: 8, top: 12, transform: [{ scale: 0.96 }], zIndex: 1 },
  stamp: { borderRadius: 10, borderWidth: 3, paddingHorizontal: 10, paddingVertical: 7, position: 'absolute', top: 28, zIndex: 5 },
  likeStamp: { borderColor: BrandColors.primary, left: 20, transform: [{ rotate: '-8deg' }] },
  skipStamp: { borderColor: '#A94C4C', right: 20, transform: [{ rotate: '8deg' }] },
  likeText: { color: BrandColors.primary, fontFamily: Fonts.rounded, fontSize: 15, fontWeight: '900' },
  skipText: { color: '#A94C4C', fontFamily: Fonts.rounded, fontSize: 17, fontWeight: '900' },
  actions: { alignItems: 'center', flexDirection: 'row', gap: 22, justifyContent: 'center', marginTop: 4, zIndex: 4 },
  action: { alignItems: 'center', backgroundColor: BrandColors.surface, borderRadius: 999, borderWidth: 1, justifyContent: 'center', shadowColor: BrandColors.shadow, shadowOffset: { width: 0, height: 5 }, shadowOpacity: 0.12, shadowRadius: 10 },
  skipAction: { borderColor: '#E8CACA', height: 58, width: 58 },
  saveAction: { borderColor: BrandColors.accentBorder, height: 50, width: 50 },
  likeAction: { borderColor: BrandColors.border, height: 58, width: 58 },
  hint: { color: BrandColors.textMuted, fontFamily: Fonts.rounded, fontSize: 11, marginTop: 14, textAlign: 'center' },
});
