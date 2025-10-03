"""
AI Streaming routes compatible with Vercel AI SDK.
Provides Server-Sent Events streaming for chat functionality.
"""

import asyncio
import json
import time
import os
from typing import AsyncGenerator, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..models.database import get_db
from ..services import LLMService
from ..schemas import (
    ContractGenerationRequest,
    ContextGenerationRequest
)

def load_system_prompt() -> str:
    """Load the detailed Cadence 1.0 system prompt from the markdown file."""
    import os
    
    # Get the project root directory (go up from src/api to project root)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    prompt_file_path = os.path.join(project_root, "prompts", "detailed_cadence_v1_system_prompt.md")
    
    try:
        with open(prompt_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Remove the markdown header if present
            if content.startswith("# Detailed Cadence 1.0 System Prompt\n"):
                content = content.replace("# Detailed Cadence 1.0 System Prompt\n", "", 1)
            return content.strip()
    except FileNotFoundError:
        # Fallback to a basic prompt if file is not found
        return "You are an expert Cadence smart contract developer. Generate secure, efficient Cadence 1.0 contracts for the Flow blockchain."
    except Exception as e:
        # Fallback to a basic prompt if there's an error
        return "You are an expert Cadence smart contract developer. Generate secure, efficient Cadence 1.0 contracts for the Flow blockchain."


router = APIRouter(prefix="/api/ai", tags=["AI Streaming"])

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: Optional[str] = "meta-llama/llama-4-scout-17b-16e-instruct"
    stream: Optional[bool] = True
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000

class ChatStreamResponse(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: list[Dict[str, Any]]

async def create_sse_response(content: str, finish_reason: Optional[str] = None) -> str:
    """Create Server-Sent Events formatted response compatible with Vercel AI SDK."""
    response_data = {
        "id": f"chatcmpl-{int(time.time())}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": "flowzmith-ai",
        "choices": [{
            "index": 0,
            "delta": {
                "content": content
            } if content else {},
            "finish_reason": finish_reason
        }]
    }
    
    if finish_reason:
        response_data["choices"][0]["delta"] = {}
        response_data["choices"][0]["finish_reason"] = finish_reason
    
    return f"data: {json.dumps(response_data)}\n\n"

async def stream_llm_response(
    prompt: str, 
    llm_service: LLMService,
    context: Optional[str] = None
) -> AsyncGenerator[str, None]:
    """Stream LLM response in SSE format compatible with Vercel AI SDK."""
    try:
        # Yield initial response
        yield await create_sse_response("")
        
        # Load system prompt from file
        system_prompt = load_system_prompt()
        
        # Build the full prompt with system prompt, context, and user prompt
        full_prompt_parts = [system_prompt]
        
        if context:
            full_prompt_parts.append(f"Context: {context}")
        
        full_prompt_parts.append(f"User Request: {prompt}")
        full_prompt = "\n\n".join(full_prompt_parts)
        
        # Get the LLM response using the system prompt
        response_text = await llm_service.generate_contract_streaming(full_prompt)
        
        # Stream the response in chunks
        chunk_size = 50
        for i in range(0, len(response_text), chunk_size):
            chunk = response_text[i:i + chunk_size]
            yield await create_sse_response(chunk)
            await asyncio.sleep(0.1)  # Small delay for realistic streaming
        
        # Send final chunk with finish reason
        yield await create_sse_response("", "stop")
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        error_response = {
            "error": {
                "message": str(e),
                "type": "server_error"
            }
        }
        yield f"data: {json.dumps(error_response)}\n\n"

@router.post("/chat/completions")
async def chat_completions(
    request: ChatRequest,
    db: Session = Depends(get_db),
    http_request: Request = None
):
    """
    OpenAI-compatible chat completions endpoint with streaming support.
    Compatible with Vercel AI SDK's useChat hook.
    """
    try:
        # Initialize LLM service
        llm_service = LLMService(db)
        
        # Get the last user message
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")
        
        latest_message = user_messages[-1].content
        
        # Build context from conversation history
        context = "\n".join([
            f"{msg.role}: {msg.content}" 
            for msg in request.messages[:-1]  # Exclude the latest message
        ])
        
        if request.stream:
            return StreamingResponse(
                stream_llm_response(latest_message, llm_service, context),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/plain; charset=utf-8",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                }
            )
        else:
            # Non-streaming response
            system_prompt = load_system_prompt()
            full_prompt_parts = [system_prompt]
            
            if context:
                full_prompt_parts.append(f"Context: {context}")
            
            full_prompt_parts.append(f"User Request: {latest_message}")
            full_prompt = "\n\n".join(full_prompt_parts)
            
            response = await llm_service.generate_contract_streaming(full_prompt)
            return {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "flowzmith-ai",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response
                    },
                    "finish_reason": "stop"
                }]
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contract/generate/stream")
async def generate_contract_stream(
    request: ContractGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Stream contract generation compatible with Vercel AI SDK.
    """
    try:
        llm_service = LLMService(db)
        
        # Load system prompt
        system_prompt = load_system_prompt()
        
        # Convert to chat format for consistency with system prompt
        prompt = f"""
        {system_prompt}
        
        User Request: Generate a Cadence smart contract with the following requirements:
        Description: {request.description}
        Network: {request.network}
        Pre-conditions: {request.pre_conditions}
        Post-conditions: {request.post_conditions}
        
        Please generate a complete Cadence smart contract based on these requirements.
        """
        
        return StreamingResponse(
            stream_llm_response(prompt, llm_service),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/plain; charset=utf-8",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/context/generate/stream")
async def generate_with_context_stream(
    request: ContextGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Stream contract generation with external context compatible with Vercel AI SDK.
    """
    try:
        llm_service = LLMService(db)
        
        # Load system prompt
        system_prompt = load_system_prompt()
        
        # Build context from markdown content and system prompt
        context = f"""
        {system_prompt}
        
        External Context:
        {request.markdown_content}
        
        Contract Requirements:
        {request.contract_requirements}
        """
        
        prompt = f"""
        Using the provided context, generate a Cadence smart contract that meets the specified requirements.
        
        Requirements: {request.contract_requirements}
        """
        
        return StreamingResponse(
            stream_llm_response(prompt, llm_service, context),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/plain; charset=utf-8",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.options("/chat/completions")
@router.options("/contract/generate/stream")
@router.options("/context/generate/stream")
async def options_handler():
    """Handle CORS preflight requests."""
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }