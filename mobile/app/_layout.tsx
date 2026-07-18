import { DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import 'react-native-reanimated';

import { BrandColors } from '@/constants/theme';
import { AppProvider } from '@/context/app-context';

export default function RootLayout() {
  const navigationTheme = {
    ...DefaultTheme,
    colors: {
      ...DefaultTheme.colors,
      background: BrandColors.background,
      primary: BrandColors.primary,
      text: BrandColors.text,
      border: BrandColors.border,
    },
  };

  return (
    <AppProvider>
      <ThemeProvider value={navigationTheme}>
        <Stack screenOptions={{ contentStyle: { backgroundColor: BrandColors.background } }}>
          <Stack.Screen name="index" options={{ headerShown: false }} />
          <Stack.Screen name="profile-setup" options={{ headerShown: false }} />
          <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
          <Stack.Screen name="event/[id]" options={{ headerShown: false }} />
          <Stack.Screen name="modal" options={{ presentation: 'modal', title: 'Modal' }} />
        </Stack>
        <StatusBar style="dark" />
      </ThemeProvider>
    </AppProvider>
  );
}
