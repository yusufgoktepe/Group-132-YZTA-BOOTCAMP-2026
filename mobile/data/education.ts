export type EducationLevel = 'associate' | 'bachelor' | 'master' | 'doctorate';

export type ProgramReference = {
  id: string;
  name: string;
  level: EducationLevel;
  duration: number;
  hasPreparatoryClass: boolean;
};

export type UniversityReference = {
  id: string;
  name: string;
  city: string;
  type: 'state' | 'foundation';
  programs: ProgramReference[];
};

export const EDUCATION_REFERENCE_VERSION = 'sample-2026-07';

// YÖK Atlas verisi içe aktarıldığında ekranlar değişmeden bu liste genişletilecek.
export const universities: UniversityReference[] = [
  {
    id: 'yok-ankara',
    name: 'Ankara Üniversitesi',
    city: 'Ankara',
    type: 'state',
    programs: [
      { id: 'ankara-computer', name: 'Bilgisayar Mühendisliği', level: 'bachelor', duration: 4, hasPreparatoryClass: true },
      { id: 'ankara-law', name: 'Hukuk', level: 'bachelor', duration: 4, hasPreparatoryClass: false },
      { id: 'ankara-medicine', name: 'Tıp', level: 'bachelor', duration: 6, hasPreparatoryClass: false },
    ],
  },
  {
    id: 'yok-bogazici',
    name: 'Boğaziçi Üniversitesi',
    city: 'İstanbul',
    type: 'state',
    programs: [
      { id: 'bogazici-computer', name: 'Bilgisayar Mühendisliği', level: 'bachelor', duration: 4, hasPreparatoryClass: true },
      { id: 'bogazici-business', name: 'İşletme', level: 'bachelor', duration: 4, hasPreparatoryClass: true },
      { id: 'bogazici-psychology', name: 'Psikoloji', level: 'bachelor', duration: 4, hasPreparatoryClass: true },
    ],
  },
  {
    id: 'yok-hacettepe',
    name: 'Hacettepe Üniversitesi',
    city: 'Ankara',
    type: 'state',
    programs: [
      { id: 'hacettepe-ai', name: 'Yapay Zekâ Mühendisliği', level: 'bachelor', duration: 4, hasPreparatoryClass: true },
      { id: 'hacettepe-medicine', name: 'Tıp', level: 'bachelor', duration: 6, hasPreparatoryClass: false },
      { id: 'hacettepe-design', name: 'Grafik Tasarımı', level: 'bachelor', duration: 4, hasPreparatoryClass: false },
    ],
  },
  {
    id: 'yok-itu',
    name: 'İstanbul Teknik Üniversitesi',
    city: 'İstanbul',
    type: 'state',
    programs: [
      { id: 'itu-computer', name: 'Bilgisayar Mühendisliği', level: 'bachelor', duration: 4, hasPreparatoryClass: true },
      { id: 'itu-industrial', name: 'Endüstri Mühendisliği', level: 'bachelor', duration: 4, hasPreparatoryClass: true },
      { id: 'itu-architecture', name: 'Mimarlık', level: 'bachelor', duration: 4, hasPreparatoryClass: true },
    ],
  },
  {
    id: 'yok-iyte',
    name: 'İzmir Yüksek Teknoloji Enstitüsü',
    city: 'İzmir',
    type: 'state',
    programs: [
      { id: 'iyte-computer', name: 'Bilgisayar Mühendisliği', level: 'bachelor', duration: 4, hasPreparatoryClass: true },
      { id: 'iyte-molecular', name: 'Moleküler Biyoloji ve Genetik', level: 'bachelor', duration: 4, hasPreparatoryClass: true },
      { id: 'iyte-architecture', name: 'Mimarlık', level: 'bachelor', duration: 4, hasPreparatoryClass: true },
    ],
  },
  {
    id: 'yok-yildiz',
    name: 'Yıldız Teknik Üniversitesi',
    city: 'İstanbul',
    type: 'state',
    programs: [
      { id: 'yildiz-computer', name: 'Bilgisayar Mühendisliği', level: 'bachelor', duration: 4, hasPreparatoryClass: true },
      { id: 'yildiz-electrical', name: 'Elektrik Mühendisliği', level: 'bachelor', duration: 4, hasPreparatoryClass: true },
      { id: 'yildiz-interactive', name: 'İnteraktif Medya Tasarımı', level: 'bachelor', duration: 4, hasPreparatoryClass: false },
    ],
  },
];

export function getClassYearOptions(program?: ProgramReference) {
  if (!program) return [];
  const years = Array.from({ length: program.duration }, (_, index) => String(index + 1));
  return program.hasPreparatoryClass ? ['prep', ...years] : years;
}
