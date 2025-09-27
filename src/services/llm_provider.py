"""
LLM Provider abstraction layer for Flowzmith.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LLMProviderType(str, Enum):
    """Supported LLM provider types."""
    OPENAI = "OPENAI"
    GROQ = "GROQ"


class PromptTemplate(BaseModel):
    """Prompt template for contract generation."""
    name: str
    template: str
    variables: List[str]
    description: Optional[str] = None


class LLMResponse(BaseModel):
    """Standardized LLM response."""
    content: str
    provider: LLMProviderType
    model: str
    tokens_used: int
    cost: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.validate_credentials()

    @abstractmethod
    def validate_credentials(self) -> bool:
        """Validate API credentials."""
        pass

    @abstractmethod
    async def generate_contract(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate contract code."""
        pass

    @abstractmethod
    async def analyze_deployment_logs(
        self,
        logs: str,
        contract_code: str
    ) -> LLMResponse:
        """Analyze deployment logs for learning."""
        pass

    @abstractmethod
    async def validate_configuration(
        self,
        config: Dict[str, Any],
        contract_code: str
    ) -> LLMResponse:
        """Validate generated configuration."""
        pass


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""

    _providers: Dict[LLMProviderType, type] = {}

    @classmethod
    def register_provider(cls, provider_type: LLMProviderType, provider_class: type):
        """Register a provider class."""
        cls._providers[provider_type] = provider_class

    @classmethod
    def create_provider(
        cls,
        provider_type: LLMProviderType,
        api_key: str,
        model: str
    ) -> LLMProvider:
        """Create a provider instance."""
        if provider_type not in cls._providers:
            raise ValueError(f"Unknown provider type: {provider_type}")

        return cls._providers[provider_type](api_key, model)


class PromptTemplateManager:
    """Manages prompt templates for contract generation."""

    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_default_templates()

    def _load_default_templates(self):
        """Load default prompt templates."""
        # Cadence contract generation template
        self.templates["cadence_contract"] = PromptTemplate(
            name="cadence_contract",
            template="""You are an expert Cadence smart contract developer for the Flow blockchain.

Generate a complete Cadence smart contract based on the following requirements:

{requirements}

The contract should:
1. Follow Cadence best practices
2. Include proper error handling
3. Be deployable on Flow testnet/mainnet
4. Include necessary resource definitions and interfaces
5. Add comments for complex logic

Contract requirements:
{requirements}

Additional context:
- Pre-conditions: {pre_conditions}
- Post-conditions: {post_conditions}

Return only the Cadence contract code without any explanations.""",
            variables=["requirements", "pre_conditions", "post_conditions"],
            description="Template for generating Cadence smart contracts"
        )

        # New: Cadence contract generation template with external context
        self.templates["cadence_contract_with_context"] = PromptTemplate(
            name="cadence_contract_with_context",
            template="""You are an expert Cadence smart contract developer for the Flow blockchain.

Use the provided external markdown context to guide the design, APIs, transactions, and scripts:

=== External Context Start ===
{external_context}
=== External Context End ===

Now generate a complete Cadence smart contract based on these requirements:
{requirements}

The contract should:
1. Strictly follow Cadence best practices and Flow project layout
2. Include proper error handling and capability/security checks
3. Be deployable on Flow (testnet/mainnet/emulator)
4. Include necessary resource definitions, interfaces, and events
5. Provide example transactions and scripts as comments where relevant

Additional context:
- Pre-conditions: {pre_conditions}
- Post-conditions: {post_conditions}

Return only the Cadence contract code without any explanations.""",
            variables=["requirements", "external_context", "pre_conditions", "post_conditions"],
            description="Template for generating Cadence contracts using external context"
        )

        # Configuration generation template
        self.templates["flow_config"] = PromptTemplate(
            name="flow_config",
            template="""Generate a flow.json configuration file for the following Cadence smart contract:

Contract Code:
{contract_code}

The configuration should:
1. Define all contract interfaces properly
2. Include network configurations for testnet/mainnet
3. Set appropriate deployment accounts
4. Include proper aliases for all deployed contracts

Return only the valid JSON configuration.""",
            variables=["contract_code"],
            description="Template for generating flow.json configurations"
        )

        # Log analysis template
        self.templates["log_analysis"] = PromptTemplate(
            name="log_analysis",
            template="""Analyze the following deployment logs for the Cadence smart contract:

Contract Code:
{contract_code}

Deployment Logs:
{logs}

Identify:
1. Error patterns and their causes
2. Success patterns that worked well
3. Optimization opportunities
4. Security considerations

Provide insights in JSON format with pattern types and confidence scores.""",
            variables=["contract_code", "logs"],
            description="Template for analyzing deployment logs"
        )

    def get_template(self, name: str) -> PromptTemplate:
        """Get a prompt template by name."""
        if name not in self.templates:
            raise ValueError(f"Template not found: {name}")
        return self.templates[name]

    def format_prompt(
        self,
        template_name: str,
        **kwargs
    ) -> str:
        """Format a prompt template with variables."""
        template = self.get_template(template_name)

        # Validate all required variables are provided
        missing_vars = set(template.variables) - set(kwargs.keys())
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")

        # Apply context truncation for templates with external_context
        if template_name == "cadence_contract_with_context" and "external_context" in kwargs:
            kwargs["external_context"] = self._truncate_context(kwargs["external_context"])

        return template.template.format(**kwargs)

    def _truncate_context(self, context: str, max_chars: int = 15000) -> str:
        """
        Truncate external context to fit within API limits while preserving important information.
        
        Args:
            context: The external context string
            max_chars: Maximum characters to keep (default 15000 for Groq API)
        
        Returns:
            Truncated context string
        """
        if len(context) <= max_chars:
            return context
        
        logger.warning(f"Context too large ({len(context)} chars), truncating to {max_chars} chars")
        
        # Try to preserve structure by keeping the beginning and important sections
        lines = context.split('\n')
        truncated_lines = []
        current_length = 0
        
        # Keep important sections (headers, code blocks, etc.)
        for line in lines:
            line_length = len(line) + 1  # +1 for newline
            
            # Always keep headers and important markers
            if (line.strip().startswith('#') or 
                line.strip().startswith('```') or 
                line.strip().startswith('## ') or
                line.strip().startswith('### ') or
                'contract' in line.lower() or
                'cadence' in line.lower() or
                'flow' in line.lower()):
                if current_length + line_length <= max_chars:
                    truncated_lines.append(line)
                    current_length += line_length
                else:
                    break
            # Keep regular lines if we have space
            elif current_length + line_length <= max_chars:
                truncated_lines.append(line)
                current_length += line_length
            else:
                break
        
        truncated_context = '\n'.join(truncated_lines)
        
        # Add truncation notice
        if len(truncated_context) < len(context):
            truncated_context += f"\n\n[... Context truncated from {len(context)} to {len(truncated_context)} characters for API limits ...]"
        
        return truncated_context

    def add_template(self, template: PromptTemplate):
        """Add a custom prompt template."""
        self.templates[template.name] = template