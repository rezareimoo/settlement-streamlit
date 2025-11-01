import { NextResponse } from 'next/server';
import { deleteCustomData, fetchCustomDataByCaseId } from '@/lib/queries';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ caseId: string }> }
) {
  try {
    const { caseId } = await params;
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

export async function DELETE(
  request: Request,
  { params }: { params: Promise<{ caseId: string }> }
) {
  try {
    const { caseId } = await params;
    const success = await deleteCustomData(caseId);

    if (success) {
      return NextResponse.json({ message: 'Custom data deleted successfully' });
    } else {
      return NextResponse.json(
        { error: 'Custom data not found or already deleted' },
        { status: 404 }
      );
    }
  } catch (error) {
    console.error('Error deleting custom data:', error);
    return NextResponse.json(
      { error: 'Failed to delete custom data' },
      { status: 500 }
    );
  }
}
