import { NextResponse } from 'next/server';
import { fetchEducation } from '@/lib/queries';

export async function GET() {
  try {
    const education = await fetchEducation();
    return NextResponse.json({ data: education });
  } catch (error) {
    console.error('Error fetching education:', error);
    return NextResponse.json(
      { error: 'Failed to fetch education data' },
      { status: 500 }
    );
  }
}
