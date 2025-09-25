"""
OpenAI LLM provider implementation.
"""

import openai
from typing import Dict, Any, Optional
import logging
from .llm_provider import LLMProvider, LLMProviderType, LLMResponse

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation."""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__(api_key, model)
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)

    def validate_credentials(self) -> bool:
        """Validate OpenAI API credentials."""
        try:
            # Try a simple API call to validate credentials
            response = self.client.models.list()
            logger.info(f"OpenAI credentials validated. Model: {self.model}")
            return True
        except Exception as e:
            logger.error(f"OpenAI credential validation failed: {e}")
            raise ValueError(f"Invalid OpenAI API key: {e}")

    async def generate_contract(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate contract code using OpenAI."""
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
                frequency_penalty=0.1,
                presence_penalty=0.1
            )

            # Calculate approximate cost (may vary based on exact model)
            cost = self._calculate_cost(response.usage.total_tokens)

            return LLMResponse(
                content=response.choices[0].message.content,
                provider=LLMProviderType.OPENAI,
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
            logger.error(f"OpenAI contract generation failed: {e}")
            raise RuntimeError(f"OpenAI API error: {e}")

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
            logger.error(f"OpenAI log analysis failed: {e}")
            raise RuntimeError(f"OpenAI log analysis error: {e}")

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
            logger.error(f"OpenAI configuration validation failed: {e}")
            raise RuntimeError(f"OpenAI validation error: {e}")

    def _calculate_cost(self, total_tokens: int) -> float:
        """Calculate approximate cost for OpenAI API usage."""
        # Cost estimates (may vary based on exact model and region)
        if self.model.startswith("gpt-4"):
            # GPT-4: ~$0.03 per 1K tokens (input), $0.06 per 1K tokens (output)
            return total_tokens * 0.000045  # Average rate
        elif self.model.startswith("gpt-3.5"):
            # GPT-3.5: ~$0.0015 per 1K tokens (input), $0.002 per 1K tokens (output)
            return total_tokens * 0.00000175  # Average rate
        else:
            # Default fallback rate
            return total_tokens * 0.00002


# Register the provider
from .llm_provider import LLMProviderFactory
LLMProviderFactory.register_provider(LLMProviderType.OPENAI, OpenAIProvider)