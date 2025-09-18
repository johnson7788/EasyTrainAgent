import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest, { params }: { params: { pid: string } }) {
  const backendUrl = process.env.BACKEND_URL;
  if (!backendUrl) {
    return NextResponse.json({ error: 'Backend URL is not configured' }, { status: 500 });
  }

  const { pid } = params;

  try {
    const response = await fetch(`${backendUrl}/api/projects/${pid}/config`);
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to connect to backend' }, { status: 500 });
  }
}

export async function PUT(request: NextRequest, { params }: { params: { pid: string } }) {
  const backendUrl = process.env.BACKEND_URL;
  if (!backendUrl) {
    return NextResponse.json({ error: 'Backend URL is not configured' }, { status: 500 });
  }

  const { pid } = params;

  try {
    const body = await request.json();
    const response = await fetch(`${backendUrl}/api/projects/${pid}/config`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to connect to backend' }, { status: 500 });
  }
}
