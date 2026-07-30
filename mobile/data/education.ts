import educationReference from '@/data/education-reference.generated.json';

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

export const EDUCATION_REFERENCE_VERSION = educationReference.metadata.referenceVersion;
export const EDUCATION_REFERENCE_UPDATED_AT = educationReference.metadata.updatedAt;
export const EDUCATION_REFERENCE_SOURCE = educationReference.metadata.sourceLabel;

export const universities = educationReference.universities as UniversityReference[];

export function getClassYearOptions(program?: ProgramReference) {
  if (!program) return [];
  const years = Array.from({ length: program.duration }, (_, index) => String(index + 1));
  return program.hasPreparatoryClass ? ['prep', ...years] : years;
}
