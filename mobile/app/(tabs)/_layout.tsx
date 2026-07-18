import { Ionicons } from '@expo/vector-icons';
import { Tabs } from 'expo-router';

import { HapticTab } from '@/components/haptic-tab';
import { BrandColors, Fonts } from '@/constants/theme';

export default function TabLayout() {
  return (
    <Tabs screenOptions={{
      headerShown: false,
      tabBarActiveTintColor: BrandColors.primary,
      tabBarInactiveTintColor: BrandColors.placeholder,
      tabBarButton: HapticTab,
      tabBarLabelStyle: { fontFamily: Fonts.rounded, fontSize: 11, fontWeight: '700', marginTop: 2 },
      tabBarStyle: { backgroundColor: BrandColors.surface, borderTopColor: BrandColors.border, height: 82, paddingBottom: 22, paddingTop: 9 },
    }}>
      <Tabs.Screen name="index" options={{
        title: 'Keşfet',
        tabBarIcon: ({ color, focused }) => <Ionicons color={color} name={focused ? 'compass' : 'compass-outline'} size={25} />,
      }} />
      <Tabs.Screen name="saved" options={{
        title: 'Kaydedilenler',
        tabBarIcon: ({ color, focused }) => <Ionicons color={color} name={focused ? 'bookmark' : 'bookmark-outline'} size={23} />,
      }} />
    </Tabs>
  );
}
