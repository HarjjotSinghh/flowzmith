import { streamText } from 'ai';
import { createStreamableValue } from 'ai/rsc';
import { StreamingTextResponse, Message } from 'ai';

export const maxDuration = 30;

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();

    // Simulate LangChain streaming response for demo purposes
    // In a real implementation, you would integrate with actual LangChain
    const stream = createStreamableValue('');

    // Mock streaming response
    const responseText = `I'm processing your request through a LangChain stream...

Here's a sample Cadence smart contract that demonstrates the concept:

\`\`\`cadence
pub contract ExampleContract {

    pub var totalSupply: UInt64

    pub resource NFT {
        pub let id: UInt64

        init(id: UInt64) {
            self.id = id
            ExampleContract.totalSupply = ExampleContract.totalSupply + 1
        }

        destroy() {
            ExampleContract.totalSupply = ExampleContract.totalSupply - 1
        }
    }

    pub fun createNFT(): @NFT {
        return <- create NFT(id: ExampleContract.totalSupply + 1)
    }

    init() {
        self.totalSupply = 0
    }
}
\`\`\`

This contract demonstrates basic resource management in Cadence with proper initialization and destruction patterns.`;

    // Simulate streaming by sending chunks
    let currentIndex = 0;
    const chunkSize = 10;

    const streamInterval = setInterval(() => {
      if (currentIndex < responseText.length) {
        const chunk = responseText.substring(currentIndex, currentIndex + chunkSize);
        stream.update(chunk);
        currentIndex += chunkSize;
      } else {
        stream.done();
        clearInterval(streamInterval);
      }
    }, 50);

    return new StreamingTextResponse(stream.value);
  } catch (error) {
    console.error('LangChain API error:', error);
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}