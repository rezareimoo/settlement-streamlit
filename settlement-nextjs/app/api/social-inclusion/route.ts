import { NextResponse } from 'next/server';
import { fetchSocialInclusionAgency } from '@/lib/queries';

export async function GET() {
  try {
    const socialInclusion = await fetchSocialInclusionAgency();
    return NextResponse.json({ data: socialInclusion });
  } catch (error) {
    console.error('Error fetching social inclusion:', error);
    return NextResponse.json(
      { error: 'Failed to fetch social inclusion data' },
      { status: 500 }
    );
  }
}
