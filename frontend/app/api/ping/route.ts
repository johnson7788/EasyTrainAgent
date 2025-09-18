import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const backendUrl = process.env.BACKEND_URL;
  if (!backendUrl) {
    return NextResponse.json({ error: 'Backend URL is not configured' }, { status: 500 });
  }

  try {
    const response = await fetch(`${backendUrl}/ping`);
    const data = await response.text();
    return new Response(data, { status: response.status, headers: { 'Content-Type': 'text/plain' } });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to connect to backend' }, { status: 500 });
  }
}
