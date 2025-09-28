import { NextRequest, NextResponse } from 'next/server'
import { groq } from '@ai-sdk/groq'
import { streamText } from 'ai'

export async function GET() {
  try {
    console.log('Testing AI connection...')
    
    const result = await streamText({
      model: groq('openai/gpt-oss-20b'),
      messages: [
        {
          role: 'user',
          content: 'Hello! Can you respond with a simple greeting?'
        }
      ],
      temperature: 0.7,
    })

    return result.toTextStreamResponse()
  } catch (error) {
    console.error('AI test error:', error)
    return NextResponse.json({ 
      error: 'AI test failed',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}
