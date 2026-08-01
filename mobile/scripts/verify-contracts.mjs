import { readFileSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const requiredRoutes = [
  'app/(tabs)/index.tsx',
  'app/(tabs)/saved.tsx',
  'app/(tabs)/create.tsx',
  'app/(tabs)/participations.tsx',
  'app/event/[id].tsx',
  'app/profile-setup.tsx',
];
for (const route of requiredRoutes) {
  if (!existsSync(resolve(root, route))) throw new Error(`Eksik mobil route: ${route}`);
}

const storage = readFileSync(resolve(root, 'services/device-storage.ts'), 'utf8');
for (const contract of ['interactionKey', 'remaining.push(interaction)', 'INTERACTION_QUEUE_KEY']) {
  if (!storage.includes(contract)) throw new Error(`Offline kuyruk sözleşmesi eksik: ${contract}`);
}

const eventApi = readFileSync(resolve(root, 'services/events-api.ts'), 'utf8');
for (const endpoint of ['/events', '/apply', '/participations', '/ratings']) {
  if (!eventApi.includes(endpoint)) throw new Error(`Mobil event API sözleşmesi eksik: ${endpoint}`);
}

const interactionApi = readFileSync(resolve(root, 'services/interactions-api.ts'), 'utf8');
for (const field of ['interaction_key', 'feed_token', 'dwell_ms']) {
  if (!interactionApi.includes(field)) throw new Error(`Interaction alanı eksik: ${field}`);
}

const accessibleFiles = [
  'components/event-card.tsx',
  'components/swipe-deck.tsx',
  'app/(tabs)/create.tsx',
  'app/(tabs)/participations.tsx',
  'app/event/[id].tsx',
];
for (const file of accessibleFiles) {
  const source = readFileSync(resolve(root, file), 'utf8');
  if (!source.includes('accessibilityRole') || !source.includes('accessibilityLabel')) {
    throw new Error(`Erişilebilirlik sözleşmesi eksik: ${file}`);
  }
}

console.log(`MOBILE_CONTRACTS_OK routes=${requiredRoutes.length} accessibility=${accessibleFiles.length}`);
