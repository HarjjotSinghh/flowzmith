import { streamText } from 'ai';

export const maxDuration = 30;

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();

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

    // Create a readable stream
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        let currentIndex = 0;
        const chunkSize = 10;

        const sendChunk = () => {
          if (currentIndex < responseText.length) {
            const chunk = responseText.substring(currentIndex, currentIndex + chunkSize);
            controller.enqueue(encoder.encode(chunk));
            currentIndex += chunkSize;
            setTimeout(sendChunk, 50);
          } else {
            controller.close();
          }
        };

        sendChunk();
      }
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Transfer-Encoding': 'chunked',
      },
    });
  } catch (error) {
    console.error('LangChain API error:', error);
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}