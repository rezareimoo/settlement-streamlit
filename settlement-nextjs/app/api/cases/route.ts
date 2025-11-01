import { NextResponse } from 'next/server';
import { fetchSettlementCases } from '@/lib/queries';

export async function GET() {
  try {
    const cases = await fetchSettlementCases();
    return NextResponse.json({ data: cases });
  } catch (error) {
    console.error('Error fetching cases:', error);
    return NextResponse.json(
      { error: 'Failed to fetch cases' },
      { status: 500 }
    );
  }
}
