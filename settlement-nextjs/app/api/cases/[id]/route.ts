import { NextResponse } from 'next/server';
import { fetchCaseById } from '@/lib/queries';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const caseData = await fetchCaseById(id);
    
    if (!caseData) {
      return NextResponse.json(
        { error: 'Case not found' },
        { status: 404 }
      );
    }
    
    return NextResponse.json({ data: caseData });
  } catch (error) {
    console.error('Error fetching case:', error);
    return NextResponse.json(
      { error: 'Failed to fetch case' },
      { status: 500 }
    );
  }
}
