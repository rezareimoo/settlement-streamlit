import { NextResponse } from 'next/server';
import { fetchPhysicalMentalHealth } from '@/lib/queries';

export async function GET() {
  try {
    const health = await fetchPhysicalMentalHealth();
    return NextResponse.json({ data: health });
  } catch (error) {
    console.error('Error fetching health:', error);
    return NextResponse.json(
      { error: 'Failed to fetch health data' },
      { status: 500 }
    );
  }
}
