"""
Streaming LLM provider wrapper for real-time contract generation with progress tracking.
"""

from typing import AsyncGenerator, Optional, Dict, Any, Callable
import asyncio
import logging
from abc import ABC, abstractmethod
from tqdm.asyncio import tqdm_asyncio

from .llm_provider import LLMProvider, LLMResponse, LLMProviderType

logger = logging.getLogger(__name__)


class StreamingLLMProvider(ABC):
    """Abstract base class for streaming LLM providers."""
    
    def __init__(self, base_provider: LLMProvider):
        self.base_provider = base_provider
        self.model = base_provider.model
        self.provider_type = base_provider.provider_type
    
    @abstractmethod
    async def generate_contract_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> AsyncGenerator[str, None]:
        """Generate contract code with streaming support and progress tracking."""
        pass


class StreamingOpenAIProvider(StreamingLLMProvider):
    """Streaming wrapper for OpenAI provider."""
    
    def __init__(self, base_provider: LLMProvider):
        super().__init__(base_provider)
        self.client = base_provider.client
    
    async def generate_contract_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> AsyncGenerator[str, None]:
        """Generate contract code with streaming support."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Estimate total tokens for progress tracking
            estimated_total = len(prompt.split()) * 2  # Rough estimate
            
            # Create streaming response
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or 4000,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1,
                stream=True
            )
            
            accumulated_content = ""
            chunk_count = 0
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    accumulated_content += content
                    chunk_count += 1
                    
                    # Calculate progress (rough estimate)
                    progress = min((chunk_count * 10) / estimated_total, 0.95)  # Cap at 95%
                    
                    if progress_callback:
                        progress_callback("generating_contract", progress)
                    
                    yield content
            
            # Signal completion
            if progress_callback:
                progress_callback("generating_contract", 1.0)
                
        except Exception as e:
            logger.error(f"OpenAI streaming generation failed: {e}")
            raise RuntimeError(f"OpenAI streaming API error: {e}")


class StreamingGroqProvider(StreamingLLMProvider):
    """Streaming wrapper for Groq provider."""
    
    def __init__(self, base_provider: LLMProvider):
        super().__init__(base_provider)
        self.client = base_provider.client
    
    async def generate_contract_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> AsyncGenerator[str, None]:
        """Generate contract code with streaming support."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Estimate total tokens for progress tracking
            estimated_total = len(prompt.split()) * 2  # Rough estimate
            
            # Create streaming response
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or 4000,
                top_p=0.9,
                stream=True
            )
            
            accumulated_content = ""
            chunk_count = 0
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    accumulated_content += content
                    chunk_count += 1
                    
                    # Calculate progress (rough estimate)
                    progress = min((chunk_count * 10) / estimated_total, 0.95)  # Cap at 95%
                    
                    if progress_callback:
                        progress_callback("generating_contract", progress)
                    
                    yield content
            
            # Signal completion
            if progress_callback:
                progress_callback("generating_contract", 1.0)
                
        except Exception as e:
            logger.error(f"Groq streaming generation failed: {e}")
            raise RuntimeError(f"Groq streaming API error: {e}")


class StreamingProgressTracker:
    """Progress tracker for streaming operations with tqdm integration."""
    
    def __init__(self, total_steps: int = 100, description: str = "Processing"):
        self.total_steps = total_steps
        self.description = description
        self.current_step = 0
        self.progress_bar = None
        self.current_phase = ""
        self.phase_progress = {}
        
    def start(self):
        """Start the progress tracking."""
        self.progress_bar = tqdm_asyncio(
            total=self.total_steps,
            desc=self.description,
            unit="%",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
        )
        return self
    
    def update_phase(self, phase: str, progress: float):
        """Update progress for a specific phase."""
        self.current_phase = phase
        self.phase_progress[phase] = progress
        
        # Map phases to overall progress ranges
        phase_ranges = {
            "preparing": (0, 10),
            "generating_contract": (10, 70),
            "generating_config": (70, 90),
            "validating": (90, 95),
            "saving": (95, 100)
        }
        
        if phase in phase_ranges:
            start, end = phase_ranges[phase]
            phase_progress_scaled = start + (end - start) * progress
            
            # Only update if we're making progress
            if phase_progress_scaled > self.current_step:
                self.current_step = phase_progress_scaled
                if self.progress_bar:
                    self.progress_bar.n = int(self.current_step)
                    self.progress_bar.set_description(f"{self.description} - {phase.replace('_', ' ').title()}")
                    self.progress_bar.refresh()
    
    def complete(self):
        """Mark the progress as complete."""
        if self.progress_bar:
            self.progress_bar.n = self.total_steps
            self.progress_bar.set_description(f"{self.description} - Complete")
            self.progress_bar.refresh()
            self.progress_bar.close()
    
    def __enter__(self):
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.complete()


class StreamingLLMService:
    """Service that provides streaming capabilities for LLM operations."""
    
    def __init__(self, base_providers: Dict[LLMProviderType, LLMProvider]):
        self.streaming_providers = {}
        
        # Wrap each provider with streaming capabilities
        for provider_type, provider in base_providers.items():
            if provider_type == LLMProviderType.OPENAI:
                self.streaming_providers[provider_type] = StreamingOpenAIProvider(provider)
            elif provider_type == LLMProviderType.GROQ:
                self.streaming_providers[provider_type] = StreamingGroqProvider(provider)
            else:
                logger.warning(f"Streaming not supported for provider: {provider_type}")
    
    def get_streaming_provider(self, provider_type: LLMProviderType) -> Optional[StreamingLLMProvider]:
        """Get a streaming provider by type."""
        return self.streaming_providers.get(provider_type)
    
    async def generate_contract_with_streaming(
        self,
        provider_type: LLMProviderType,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        progress_tracker: Optional[StreamingProgressTracker] = None
    ) -> AsyncGenerator[str, None]:
        """Generate contract with streaming and progress tracking."""
        provider = self.get_streaming_provider(provider_type)
        if not provider:
            raise ValueError(f"Streaming not supported for provider: {provider_type}")
        
        # Define progress callback
        def progress_callback(phase: str, progress: float):
            if progress_tracker:
                progress_tracker.update_phase(phase, progress)
        
        # Stream the generation
        async for chunk in provider.generate_contract_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            progress_callback=progress_callback
        ):
            yield chunk