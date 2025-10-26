import { NextResponse } from 'next/server';
import { fetchJamatiMembers } from '@/lib/queries';

export async function GET() {
  try {
    const members = await fetchJamatiMembers();
    return NextResponse.json({ data: members });
  } catch (error) {
    console.error('Error fetching members:', error);
    return NextResponse.json(
      { error: 'Failed to fetch members' },
      { status: 500 }
    );
  }
}
