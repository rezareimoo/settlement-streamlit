import { NextResponse } from 'next/server';
import { fetchFDPCases } from '@/lib/queries';

export async function GET() {
  try {
    const fdpCases = await fetchFDPCases();
    return NextResponse.json({ data: fdpCases });
  } catch (error) {
    console.error('Error fetching FDP cases:', error);
    return NextResponse.json(
      { error: 'Failed to fetch FDP cases' },
      { status: 500 }
    );
  }
}
