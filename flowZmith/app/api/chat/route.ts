import { groq } from '@ai-sdk/groq'
import { streamText } from 'ai'
import { auth } from '@/lib/auth'
import { userQueries } from '@/lib/db/queries'

// Allow streaming responses up to 30 seconds
export const maxDuration = 30

export async function POST(req: Request) {
  try {
    // Check authentication
    const session = await auth()
    if (!session?.user?.email) {
      return new Response(
        JSON.stringify({ error: 'Unauthorized' }),
        { status: 401, headers: { 'Content-Type': 'application/json' } }
      )
    }

    // Get user from database
    const user = await userQueries.findByEmail(session.user.email)
    if (!user) {
      return new Response(
        JSON.stringify({ error: 'User not found' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      )
    }

    // Check if user has credits remaining
    if ((user.requestsUsed || 0) >= (user.requestsLimit || 0)) {
      return new Response(
        JSON.stringify({ 
          error: 'No credits remaining',
          credits: {
            used: user.requestsUsed || 0,
            limit: user.requestsLimit || 0,
            remaining: 0
          }
        }),
        { status: 429, headers: { 'Content-Type': 'application/json' } }
      )
    }

    const { messages } = await req.json()

    // Get the last user message
    const lastMessage = messages[messages.length - 1]

    // Add context about Flow blockchain and Cadence
    const systemPrompt = `You are an expert Flow blockchain developer specializing in Cadence smart contracts.
IMPORTANT: Always generate complete, production-ready Cadence smart contract code with:
- Proper contract structure with pub fun init()
- Resource definitions with proper interfaces
- Access control (pub, access(all), etc.)
- Error handling with pre and post conditions
- Comments explaining key functionality
- Proper import statements

Always respond with:
1. A clear explanation of what the contract does
2. The complete Cadence code in a code block with \`\`\`cadence syntax
3. Any deployment considerations or usage examples

Focus on:
- NFT contracts (NonFungibleToken standard)
- Fungible Token contracts (FungibleToken standard)
- Marketplace contracts
- Staking contracts
- DAO contracts
- Simple utility contracts

Never generate incomplete code snippets. Always provide full, deployable contracts.`

    // Add system message if not present
    const enhancedMessages = messages[0]?.role === 'system'
      ? messages
      : [{ role: 'system', content: systemPrompt }, ...messages]

    const result = await streamText({
      model: groq('openai/gpt-oss-20b'),
      system: systemPrompt,
      messages: enhancedMessages,
      temperature: 0.7,
    })

    // Deduct credit after successful request
    try {
      await userQueries.update(user.id, {
        requestsUsed: (user.requestsUsed || 0) + 1
      })
      console.log(`Credit deducted for user ${user.email}. Used: ${(user.requestsUsed || 0) + 1}/${user.requestsLimit || 0}`)
    } catch (error) {
      console.error('Error deducting credit:', error)
      // Don't fail the request if credit deduction fails
    }

    return result.toTextStreamResponse()
  } catch (error) {
    console.error('Chat API error:', error)
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    )
  }
}