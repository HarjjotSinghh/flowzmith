"""
Groq LLM provider implementation.
"""

import os
from typing import Dict, Any, Optional
import logging
from .llm_provider import LLMProvider, LLMProviderType, LLMResponse

# Import Groq if available, otherwise provide fallback
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None

logger = logging.getLogger(__name__)


class GroqProvider(LLMProvider):
    """Groq API provider implementation."""

    def __init__(self, api_key: str, model: str = "llama2-70b-4096"):
        super().__init__(api_key, model)

        if not GROQ_AVAILABLE:
            raise ImportError("Groq package not installed. Install with: pip install groq")

        self.client = Groq(api_key=api_key)
        # Explicitly set provider type for downstream streaming wrappers and logging
        self.provider_type = LLMProviderType.GROQ

    def validate_credentials(self) -> bool:
        """Validate Groq API credentials."""
        try:
            # Try a simple API call to validate credentials
            models = self.client.models.list()
            logger.info(f"Groq credentials validated. Model: {self.model}")
            return True
        except Exception as e:
            logger.error(f"Groq credential validation failed: {e}")
            raise ValueError(f"Invalid Groq API key: {e}")

    async def generate_contract(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate contract code using Groq."""
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or 4000,
                top_p=0.9,
                stream=False
            )

            # Calculate approximate cost (Groq pricing may vary)
            cost = self._calculate_cost(response.usage.total_tokens)

            return LLMResponse(
                content=response.choices[0].message.content,
                provider=LLMProviderType.GROQ,
                model=self.model,
                tokens_used=response.usage.total_tokens,
                cost=cost,
                metadata={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "finish_reason": response.choices[0].finish_reason
                }
            )

        except Exception as e:
            logger.error(f"Groq contract generation failed: {e}")
            raise RuntimeError(f"Groq API error: {e}")

    async def analyze_deployment_logs(
        self,
        logs: str,
        contract_code: str
    ) -> LLMResponse:
        """Analyze deployment logs for learning."""
        try:
            system_prompt = """You are an expert Flow blockchain deployment analyst.
            Analyze deployment logs to identify patterns, errors, and optimization opportunities.
            Provide structured insights in JSON format."""

            prompt = f"""
Contract Code:
{contract_code}

Deployment Logs:
{logs}

Analyze these logs and provide insights on:
1. Error patterns and their root causes
2. Success patterns and what worked well
3. Optimization opportunities
4. Security considerations
5. Configuration improvements

Return a JSON response with these insights."""

            return await self.generate_contract(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.2
            )

        except Exception as e:
            logger.error(f"Groq log analysis failed: {e}")
            raise RuntimeError(f"Groq log analysis error: {e}")

    async def validate_configuration(
        self,
        config: Dict[str, Any],
        contract_code: str
    ) -> LLMResponse:
        """Validate generated configuration."""
        try:
            system_prompt = """You are an expert Flow blockchain configuration validator.
            Validate flow.json configurations for correctness and completeness."""

            prompt = f"""
Contract Code:
{contract_code}

Configuration:
{config}

Validate this configuration for:
1. Correct contract interface definitions
2. Proper network settings
3. Valid account addresses
4. Complete alias definitions
5. Deployment compatibility

Return a JSON response with validation results and any errors found."""

            return await self.generate_contract(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.1
            )

        except Exception as e:
            logger.error(f"Groq configuration validation failed: {e}")
            raise RuntimeError(f"Groq validation error: {e}")

    def _calculate_cost(self, total_tokens: int) -> float:
        """Calculate approximate cost for Groq API usage."""
        # Groq currently offers free tier, but we'll include cost calculation
        # for future paid tiers or usage tracking
        # This is a placeholder calculation
        return total_tokens * 0.000001  # Minimal cost calculation


# Register the provider if Groq is available
if GROQ_AVAILABLE:
    from .llm_provider import LLMProviderFactory
    LLMProviderFactory.register_provider(LLMProviderType.GROQ, GroqProvider)