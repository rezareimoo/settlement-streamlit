import { NextResponse } from 'next/server';
import { fetchCustomDataByCaseId, saveCustomData } from '@/lib/queries';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const caseId = searchParams.get('caseId');

    if (!caseId) {
      return NextResponse.json(
        { error: 'Case ID is required' },
        { status: 400 }
      );
    }

    const customData = await fetchCustomDataByCaseId(caseId);
    return NextResponse.json({ data: customData });
  } catch (error) {
    console.error('Error fetching custom data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch custom data' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { case_id, family_progress_status, languages_spoken, arrival_date } = body;

    if (!case_id || !family_progress_status || !arrival_date) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    const success = await saveCustomData({
      case_id,
      family_progress_status,
      languages_spoken: languages_spoken || [],
      arrival_date,
    });

    if (success) {
      return NextResponse.json({ message: 'Custom data saved successfully' });
    } else {
      return NextResponse.json(
        { error: 'Failed to save custom data' },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('Error saving custom data:', error);
    return NextResponse.json(
      { error: 'Failed to save custom data' },
      { status: 500 }
    );
  }
}
