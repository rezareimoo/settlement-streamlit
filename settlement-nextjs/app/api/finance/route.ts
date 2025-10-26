import { NextResponse } from 'next/server';
import { fetchFinance } from '@/lib/queries';

export async function GET() {
  try {
    const finance = await fetchFinance();
    return NextResponse.json({ data: finance });
  } catch (error) {
    console.error('Error fetching finance:', error);
    return NextResponse.json(
      { error: 'Failed to fetch finance data' },
      { status: 500 }
    );
  }
}
