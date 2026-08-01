import type { FeedItem } from '@/services/feed-api';
import type { CampusEvent, EventIcon } from '@/types/event';

const categoryMeta: Record<string, { label: string; icon: EventIcon; color: string }> = {
  technology: { label: 'Teknoloji', icon: 'sparkles', color: '#DCEFE9' },
  career: { label: 'Kariyer', icon: 'rocket', color: '#E4E7FA' },
  science: { label: 'Bilim', icon: 'sparkles', color: '#DDEAF5' },
  'design-art': { label: 'Tasarım', icon: 'color-palette', color: '#F6E2E7' },
  'sports-health': { label: 'Spor ve Sağlık', icon: 'sparkles', color: '#E3F2D8' },
  'social-impact': { label: 'Sosyal Etki', icon: 'sparkles', color: '#FFF0D9' },
  'culture-community': { label: 'Topluluk', icon: 'phone-portrait', color: '#E8E1F4' },
};

function tags(value: unknown): string[] {
  if (Array.isArray(value)) return value.map(String);
  if (typeof value !== 'string' || !value) return [];
  try {
    const parsed = JSON.parse(value);
    if (Array.isArray(parsed)) return parsed.map(String);
  } catch {
    // Eski noktalı virgül sözleşmesine düş.
  }
  return value.split(';').filter(Boolean);
}

function dateParts(value: unknown) {
  if (typeof value !== 'string' || !value) return { dateLabel: 'Tarih açıklanacak', time: '--.--' };
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return { dateLabel: value, time: '--.--' };
  return {
    dateLabel: new Intl.DateTimeFormat('tr-TR', { day: 'numeric', month: 'long' }).format(date),
    time: new Intl.DateTimeFormat('tr-TR', { hour: '2-digit', minute: '2-digit' }).format(date),
  };
}

export function mapApiEvent(raw: Record<string, unknown>, recommendation?: Omit<FeedItem, 'event'>): CampusEvent {
  const categoryId = String(raw.category_id || raw.category || 'culture-community');
  const meta = categoryMeta[categoryId] ?? categoryMeta['culture-community'];
  const participationMode = String(raw.participation_mode || raw.location_type || 'onsite') as CampusEvent['participationMode'];
  const date = dateParts(raw.starts_at || raw.date);
  const locationType = participationMode === 'online' ? 'Online' : participationMode === 'hybrid' ? 'Hibrit' : 'Kampüste';
  const interestIds = tags(raw.interest_ids || raw.target_interests);
  const goalIds = tags(raw.target_goal_ids || raw.target_goals);

  return {
    id: String(raw.event_id),
    title: String(raw.title || 'Etkinlik'),
    clubName: String(raw.club_name || 'CampusMatch Topluluğu'),
    category: meta.label,
    interestIds,
    goalIds,
    participationMode,
    feeType: String(raw.fee_type || 'free') as CampusEvent['feeType'],
    language: String(raw.language || 'tr') as CampusEvent['language'],
    ...date,
    location: String(raw.location_name || raw.location || locationType),
    locationType,
    format: String(raw.event_type || 'Etkinlik'),
    matchScore: Math.round(recommendation?.score ?? 50),
    description: String(raw.description || ''),
    tags: interestIds.slice(0, 3),
    reasons: recommendation?.reasons?.length
      ? recommendation.reasons
      : ['Kampüsünde yeni fırsatlar keşfetmen için önerildi.'],
    icon: meta.icon,
    color: meta.color,
    eventTier: raw.event_tier === 'micro' ? 'micro' : 'official',
    organizerTrustScore: Number(raw.organizer_trust_score || 0),
    participantCount: Number(raw.participant_count || 0),
  };
}

export function mapFeedItem(item: FeedItem) {
  return mapApiEvent(item.event, {
    score: item.score,
    score_breakdown: item.score_breakdown,
    reasons: item.reasons,
  });
}
