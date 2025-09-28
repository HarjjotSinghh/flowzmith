"""
OpenAI LLM provider implementation.
"""

import openai
from typing import Dict, Any, Optional
import logging
import json
from .llm_provider import PromptTemplateManager, LLMResponse, LLMProviderType, PromptTemplate
from .llm_provider import LLMProvider, LLMProviderType, LLMResponse

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation."""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__(api_key, model)
        # Explicitly set provider type for downstream streaming wrappers and logging
        self.provider_type = LLMProviderType.OPENAI
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
        prompt_manager = PromptTemplateManager()
        if system_prompt is None:
            # Use the detailed Cadence 1.0 template as default system prompt
            system_prompt = prompt_manager.get_template("cadence_v1_detailed").template
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

            # Strip markdown code blocks from contract content
            from .flow_service import strip_markdown_code_blocks
            cleaned_content = strip_markdown_code_blocks(response.choices[0].message.content)

            return LLMResponse(
                content=cleaned_content,
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
        prompt_manager = PromptTemplateManager()
        system_prompt = "You are an expert Flow blockchain deployment analyst. Analyze deployment logs to identify patterns, errors, and optimization opportunities. Provide structured insights in JSON format, ensuring Cadence 1.0 compliance checks."
        prompt_template = prompt_manager.get_template("log_analysis")
        prompt = prompt_template.template.format(contract_code=contract_code, logs=logs)
        try:
            # Use the formatted log analysis template with 1.0 awareness
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
        prompt_manager = PromptTemplateManager()
        # Adapt flow_config for validation
        validation_template = PromptTemplate(
            name="config_validation",
            template="""Validate the following flow.json configuration for the Cadence 1.0 smart contract:

Contract Code:
{contract_code}

Configuration to Validate:
{config_json}

Validation Checklist (Cadence 1.0):
1. Correct contract interface definitions (inheritance, no restricted types)
2. Proper network settings with 1.0 accounts and entitlements
3. Valid account addresses and capability controllers
4. Complete alias definitions for deployed contracts
5. Deployment compatibility (v2 token support if applicable)
6. No deprecated syntax or migration issues

Return a JSON response with:
- valid: boolean
- issues: list of problems
- suggestions: list of fixes
- compliance_score: 0-100""",
            variables=["contract_code", "config_json"],
            description="Validation template for 1.0 configs"
        )
        prompt = validation_template.template.format(
            contract_code=contract_code,
            config_json=json.dumps(config, indent=2)
        )
        system_prompt = "You are an expert Flow blockchain configuration validator for Cadence 1.0. Ensure full migration compliance."
        try:
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