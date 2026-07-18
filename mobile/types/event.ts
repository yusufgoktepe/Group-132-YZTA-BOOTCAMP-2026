export type EventIcon = 'color-palette' | 'phone-portrait' | 'rocket' | 'sparkles';

export type CampusEvent = {
  id: string;
  title: string;
  clubName: string;
  category: string;
  interestIds: string[];
  goalIds: string[];
  participationMode: 'onsite' | 'online' | 'hybrid';
  feeType: 'free' | 'paid';
  language: 'tr' | 'en' | 'mixed';
  dateLabel: string;
  time: string;
  location: string;
  locationType: 'Hibrit' | 'Kampüste' | 'Online';
  format: string;
  matchScore: number;
  description: string;
  tags: string[];
  reasons: string[];
  icon: EventIcon;
  color: string;
};
