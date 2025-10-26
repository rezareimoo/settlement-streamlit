import { query } from './db';
import {
  SettlementCase,
  JamatiMember,
  Education,
  Finance,
  PhysicalMentalHealth,
  SocialInclusionAgency,
  FDPCase,
  CustomData,
} from '@/types';

// Fetch all settlement cases
export async function fetchSettlementCases(): Promise<SettlementCase[]> {
  const result = await query<SettlementCase>('SELECT * FROM SettlementCase');
  return result.rows;
}

// Fetch all jamati members
export async function fetchJamatiMembers(): Promise<JamatiMember[]> {
  const result = await query<JamatiMember>('SELECT * FROM JamatiMember');
  return result.rows;
}

// Fetch all education records
export async function fetchEducation(): Promise<Education[]> {
  const result = await query<Education>('SELECT * FROM Education');
  return result.rows;
}

// Fetch all finance records
export async function fetchFinance(): Promise<Finance[]> {
  const result = await query<Finance>('SELECT * FROM Finance');
  return result.rows;
}

// Fetch all physical and mental health records
export async function fetchPhysicalMentalHealth(): Promise<PhysicalMentalHealth[]> {
  const result = await query<PhysicalMentalHealth>('SELECT * FROM PhysicalMentalHealth');
  return result.rows;
}

// Fetch all social inclusion agency records
export async function fetchSocialInclusionAgency(): Promise<SocialInclusionAgency[]> {
  const result = await query<SocialInclusionAgency>('SELECT * FROM SocialInclusionAgency');
  return result.rows;
}

// Fetch FDP cases
export async function fetchFDPCases(): Promise<FDPCase[]> {
  const result = await query<FDPCase>('SELECT * FROM fdp_cases');
  return result.rows;
}

// Fetch case by ID
export async function fetchCaseById(caseId: string): Promise<SettlementCase | null> {
  const result = await query<SettlementCase>(
    'SELECT * FROM SettlementCase WHERE caseid = $1',
    [caseId]
  );
  return result.rows[0] || null;
}

// Fetch custom data by case ID
export async function fetchCustomDataByCaseId(caseId: string): Promise<CustomData | null> {
  const result = await query<CustomData>(
    'SELECT * FROM custom_data WHERE case_id = $1',
    [caseId]
  );
  return result.rows[0] || null;
}

// Save custom data
export async function saveCustomData(data: CustomData): Promise<boolean> {
  try {
    // Check if record exists
    const existing = await fetchCustomDataByCaseId(data.case_id);

    if (existing) {
      // Update existing record
      await query(
        `UPDATE custom_data 
         SET family_progress_status = $1, languages_spoken = $2, arrival_date = $3
         WHERE case_id = $4`,
        [data.family_progress_status, data.languages_spoken, data.arrival_date, data.case_id]
      );
    } else {
      // Insert new record
      await query(
        `INSERT INTO custom_data (case_id, family_progress_status, languages_spoken, arrival_date)
         VALUES ($1, $2, $3, $4)`,
        [data.case_id, data.family_progress_status, data.languages_spoken, data.arrival_date]
      );
    }
    return true;
  } catch (error) {
    console.error('Error saving custom data:', error);
    return false;
  }
}

// Delete custom data
export async function deleteCustomData(caseId: string): Promise<boolean> {
  try {
    const result = await query('DELETE FROM custom_data WHERE case_id = $1', [caseId]);
    return (result.rowCount ?? 0) > 0;
  } catch (error) {
    console.error('Error deleting custom data:', error);
    return false;
  }
}

// Fetch members by case ID
export async function fetchMembersByCaseId(caseId: string): Promise<JamatiMember[]> {
  const result = await query<JamatiMember>(
    'SELECT * FROM JamatiMember WHERE caseid = $1',
    [caseId]
  );
  return result.rows;
}

// Fetch education by person ID
export async function fetchEducationByPersonId(personId: number): Promise<Education | null> {
  const result = await query<Education>(
    'SELECT * FROM Education WHERE personid = $1',
    [personId]
  );
  return result.rows[0] || null;
}

// Fetch finance by person ID
export async function fetchFinanceByPersonId(personId: number): Promise<Finance | null> {
  const result = await query<Finance>(
    'SELECT * FROM Finance WHERE personid = $1',
    [personId]
  );
  return result.rows[0] || null;
}

// Fetch physical mental health by person ID
export async function fetchHealthByPersonId(personId: number): Promise<PhysicalMentalHealth | null> {
  const result = await query<PhysicalMentalHealth>(
    'SELECT * FROM PhysicalMentalHealth WHERE personid = $1',
    [personId]
  );
  return result.rows[0] || null;
}

// Fetch social inclusion by person ID
export async function fetchSocialInclusionByPersonId(personId: number): Promise<SocialInclusionAgency | null> {
  const result = await query<SocialInclusionAgency>(
    'SELECT * FROM SocialInclusionAgency WHERE personid = $1',
    [personId]
  );
  return result.rows[0] || null;
}
