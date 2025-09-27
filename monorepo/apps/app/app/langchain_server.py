"""
LangChain Python server for smart contract generation
Run this with: python langchain_server.py
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import json
from datetime import datetime

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.callbacks.base import BaseCallbackHandler
import asyncio

app = FastAPI(title="Smart Contract LangChain API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    messages: List[dict]
    stream: bool = True

class ChatResponse(BaseModel):
    content: str
    type: str = "response"

class StreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.content = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.content += token

# Initialize the language model
llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.7,
    streaming=True,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# System prompt for smart contract generation
SYSTEM_PROMPT = """You are an expert Flow blockchain developer specializing in Cadence smart contracts.

IMPORTANT: Always generate complete, production-ready Cadence smart contract code with:
- Proper contract structure with pub fun init()
- Resource definitions with proper interfaces
- Access control (pub, access(all), etc.)
- Error handling with pre and post conditions
- Comments explaining key functionality
- Proper import statements

Always respond with:
1. A clear explanation of what the contract does
2. The complete Cadence code in a code block with ```cadence syntax
3. Any deployment considerations or usage examples

Focus on:
- NFT contracts (NonFungibleToken standard)
- Fungible Token contracts (FungibleToken standard)
- Marketplace contracts
- Staking contracts
- DAO contracts
- Simple utility contracts

Never generate incomplete code snippets. Always provide full, deployable contracts."""

@app.post("/api/langchain/chat")
async def chat_with_langchain(request: ChatRequest):
    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        # Extract messages
        messages = request.messages

        # Create LangChain messages
        langchain_messages = [SystemMessage(content=SYSTEM_PROMPT)]

        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))

        # Create callback handler for streaming
        callback_handler = StreamingCallbackHandler()

        # Generate response
        if request.stream:
            # For streaming response
            async def generate_stream():
                try:
                    async for chunk in llm.astream(langchain_messages, callbacks=[callback_handler]):
                        if chunk.content:
                            yield f"data: {json.dumps({'content': chunk.content})}\n\n"

                    # Send final message
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
            )
        else:
            # For non-streaming response
            response = await llm.ainvoke(langchain_messages)
            return ChatResponse(content=response.content)

    except Exception as e:
        print(f"LangChain API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/langchain/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)