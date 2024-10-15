import { NextResponse } from 'next/server';

export async function POST(req) {
  const { question, context } = await req.json();

  // Updated with the current ngrok URL for FastAPI
  const ngrokUrl = `${process.env.NEXT_PUBLIC_NGROK_URL}/qa/`;

  // Call the FastAPI endpoint
  const response = await fetch(ngrokUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, context }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error("Error calling FastAPI:", errorText);
    return NextResponse.json({ error: "Failed to reach FastAPI" }, { status: 500 });
  }

  const data = await response.json();
  return NextResponse.json(data);
}
