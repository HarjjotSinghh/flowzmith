import { NextRequest, NextResponse } from 'next/server'

const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://localhost:8000'

export async function GET(request: NextRequest) {
  try {
    // Forward the request to the Python backend
    const response = await fetch(`${PYTHON_BACKEND_URL}/api/v1/deployments`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const errorText = await response.text()
      return NextResponse.json(
        { error: `Backend error: ${response.statusText}`, details: errorText },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error forwarding request to Python backend:', error)
    return NextResponse.json(
      { error: 'Failed to connect to backend service' },
      { status: 500 }
    )
  }
}