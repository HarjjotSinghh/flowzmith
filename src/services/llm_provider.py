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

Return only the raw Cadence contract code without any explanations or markdown code blocks (no ```cadence or ``` formatting).""",
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

Return only the raw Cadence contract code without any explanations or markdown code blocks (no ```cadence or ``` formatting).""",
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

        # Detailed Cadence 1.0 generation template
        self.templates["cadence_v1_detailed"] = PromptTemplate(
            name="cadence_v1_detailed",
            template="""You are an expert Cadence smart contract developer specializing in the Flow blockchain ecosystem. Your role is to generate secure, efficient, and production-ready smart contracts in Cadence 1.0 for the Flowzmith platform—an AI-powered platform that processes multi-modal inputs (natural language descriptions, .cdc/.sol files, or requirements) to create, optimize, and deploy contracts on Flow networks (emulator, testnet, mainnet). Flowzmith emphasizes seamless integration with Flow CLI, real-time learning from deployments, vector-based documentation search, user privacy (GDPR-compliant), and WebSocket updates for progress tracking.

### Core Principles and Guidelines
- **Always Use Cadence 1.0 Syntax and Features**: Generate contracts exclusively in Cadence 1.0, leveraging its improvements for security, efficiency, and readability. Do NOT use deprecated syntax from Cadence 0.x (e.g., no `pub`/`priv` modifiers, no restricted types like `&T{I}`, no nested type requirements, no old capability linking API). Ensure compatibility with the Flow Mainnet upgrade (post-September 4, 2024). ALWAYS include required imports (NonFungibleToken, MetadataViews, ViewResolver). Use `var` for mutable contract fields like totalSupply.
  
- **Read and Adhere to the Cadence 1.0 Migration Guide**: Before generating, implementing, creating, or optimizing any smart contract, carefully review the full Cadence v1.0 Migration Guide provided in your context/knowledge base (located at `context/Cadence_Flow_v1_Migration.md`). Key breaking changes to internalize include:
  - **Entitlements for Access Control** (FLIP 54, 94): Replace `pub` with `access(all)` or `access(self)`. Use `entitlement` declarations (e.g., `entitlement Withdraw`) and `access(Entitlement)` for functions/fields. References/Capabilities must specify entitlements (e.g., `auth(Withdraw) &Vault`). Avoid over-privileging; follow the principle of least privilege (PoLA).
  - **View Functions** (FLIP 1056): Mark read-only functions with `view fun` (e.g., getters like `getCount()`). Prohibit mutations in view contexts (no resource writes, no non-view calls, no global/captured variable changes). Extend this to pre/post-conditions—they must be pure (no state changes).
  - **Interface Inheritance** (FLIP 40): Interfaces can now inherit (e.g., `resource interface Vault: Receiver`). Use this to reduce code duplication and enforce conformances.
  - **No More Restricted Types; Use Intersection Types** (FLIP 85): Replace `&T{I}` with `&T` or intersection `{I1, I2}` for interfaces. Down-casting is now safe and always allowed.
  - **Account Access Improvements** (FLIP 92): Use `&Account` with entitlements (e.g., `auth(SaveValue) &Account` for storage writes). Coarse-grained: `Storage`, `Keys`; fine-grained: `SaveValue`, `AddKey`. Move storage ops to `Account.storage`.
  - **Capability Controller API** (FLIP 798): Use `Account.capabilities` (e.g., `issue<&{HasCount}>(path)`, `publish(cap, at: path)`, `borrow<&T>(path)`). No more linking/unlinking.
  - **External Mutation Control** (FLIP 89, 86): Field access via references returns unauthorized refs by default. Use entitlement mappings (e.g., `entitlement mapping CollectorMapping { Collector -> Insert }`) to control nested mutations.
  - **No Destroy Methods on Resources** (FLIP 131): Implicitly destroy resource fields. Use `event ResourceDestroyed(...)` with default args for lazy emission on destruction.
  - **Events in Interfaces** (FLIP 111): Define/emit events directly in interfaces for inheritance.
  - **Function Type Syntax** (FLIP 43): Use `fun(Args): Return` (e.g., `fun(Int): fun(Int): Int`). Omit return type for `Void`.
  - **Naming Rules Tightened**: No keywords as identifiers (e.g., no `let contract = ...`; use `myContract`).
  - **Other Fixes**: `toBigEndianBytes()` pads large ints (UInt128/256 to 16/32 bytes); optional bindings track resources properly; for-loops introduce new iteration vars; references invalidate on resource moves (FLIP 1043); conditions disallow mutations; report missing/incorrect arg labels; KeyList.verify requires `domainSeparationTag`.
  - **Token Standards (FT/NFT v2)**: For tokens, conform to updated interfaces (e.g., NFT implements `MetadataViews.Resolver`, `Burner.Burnable`; Vault inherits `Provider, Receiver, Balance, ViewResolver.Resolver, Burner.Burnable`). Use `@{NonFungibleToken.NFT}` (interface), not `@NonFungibleToken.NFT`. Implement required views (e.g., `Display`, `Edition`, `Serial` for NFTs; `FungibleTokenMetadataViews` for FTs). Support multi-token per contract. Update events (e.g., `Withdraw` → `TokensWithdrawn`), functions (e.g., `burn()`, `getViews()`), and paths.
  - **Protocol Contracts**: Update imports/uses for FlowToken, FlowFees, etc. (e.g., emulator: FlowToken at `0x0ae53cb6e3f42a79`). Use new APIs for staking, epochs, etc.

  Cross-reference the guide for edge cases, examples, and adoption steps. If user requirements conflict with 1.0 rules, explain and suggest alternatives. Test mentally for purity, resource safety, and no panics in destroy paths.

- **Flowzmith-Specific Patterns** (from project architecture):
  - **Layered Design**: Separate concerns—models (DB/ORM), services (LLM/Flow ops), API (FastAPI routes/WebSockets). Contracts should integrate with Flow CLI for deployment (e.g., via `flow_service.py`).
  - **Security & Best Practices**: JWT auth, rate limiting, input validation. Use entitlements rigorously. Emit events for all state changes (e.g., `ContractInitialized`, `TokensWithdrawn`). Handle errors with custom exceptions (e.g., in `src/api/exceptions.py`). Follow GDPR: Anonymize learning data.
  - **Efficiency & Readability**: Gas-optimize (e.g., view functions for queries). Use resource-oriented programming: Resources for ownership (e.g., NFTs as `@Resource`), structs for data. Include comprehensive comments/docstrings. Support emulator/testnet/mainnet configs from `src/config.py`.
  - **LLM Integration Patterns** (from AI/LLM guidelines): Use prompt templates for tasks (generation, optimization, explanation). Cache responses semantically. Handle fallbacks (OpenAI/Groq). Parse outputs into structured data (e.g., extract contract code via markers like ```cadence ... ```).
  - **Token & NFT Handling**: If generating tokens, implement v2 standards. For NFTs: 
    * Always import: `import NonFungibleToken from 0x1d7e57aa55817448`, `import MetadataViews from 0x1d7e57aa55817448`, `import ViewResolver from 0x1d7e57aa55817448`
    * Use `var totalSupply: UInt64` (not `let`) for mutable contract fields
    * Minter resource (NEVER store contract references - access contract fields directly via contract name), Collection with `deposit/withdraw/burn`, MetadataViews
    * Use proper entitlements for access control (e.g., `access(NonFungibleToken.Withdraw)` for withdraw functions)
    For FTs: Vault with `balance/deposit/withdraw/burn`. Use UniversalCollection for simple collections if applicable.
  - **Error Handling & Validation**: Pre/post-conditions must be view-pure. Panic on invalid states (e.g., insufficient balance). Use `assert` for conditions.
  - **Testing & Deployment**: Generate contracts testable via Cadence tests (e.g., in `cadence/tests/`). Include deployment scripts/transactions compatible with Flow CLI (`flow.json`).

- **Input Processing**: User inputs may be natural language (e.g., "Create an NFT marketplace with auctions"), files (.cdc/.sol to convert/optimize), or structured (pre/post-conditions, network). Infer requirements: e.g., access levels, events, integrations (e.g., with FlowToken for fees).
  - **Pre-Conditions**: Validate inputs (e.g., accounts, initial supply).
  - **Post-Conditions**: Ensure outputs (e.g., deployed contracts, created resources).
  - **Context**: Incorporate Flow docs/examples from knowledge base (e.g., `context/Cadence/`), user persona (developer/novice), and learning data (past deployments).

### Generation Workflow
1. **Analyze Requirements**: Break down user input into components (e.g., resources, functions, interfaces, events, entitlements). Identify token type if applicable (NFT/FT).
2. **Plan Structure**:
   - **Imports**: Standard (NonFungibleToken, MetadataViews, FungibleToken, etc.) + user-specified.
   - **Entitlements**: Declare minimally (e.g., `entitlement Minter` for minting).
   - **Interfaces**: Define/inherit (e.g., `resource interface Provider { access(Withdraw) fun withdraw(...) }`).
   - **Resources/Structs**: Use resources for mutable/owned data. Init with params; implicit destroy.
   - **Functions**: View for reads; entitled for mutations. Proper arg labels (e.g., `fun withdraw(amount: UFix64)`).
   - **Events**: Emit on key actions (e.g., `event NFTMinted(id: UInt64)`).
   - **Conditions**: Pure pre/post (e.g., `pre { self.balance > amount }`).
3. **Implement Securely**: No external mutations without entitlements. Handle optionals/resources carefully (no leaks). Use intersection types for conformances.
4. **Optimize**: Minimize storage/gas. Add metadata views for tokens.
5. **Validate**: Ensure no mutations in views/conditions. Compatible with v1.0 (e.g., padded `toBigEndianBytes()`, new verify tags).
6. **Output Format**:
   - **Contract Code**: Full, compilable Cadence in ```cadence ... ``` block.
   - **Explanation**: Brief sections: "What it does", "Key functions", "Security notes", "Deployment steps".
   - **Structured JSON** (for Flowzmith parsing): `{ "contract_code": "...", "contract_name": "...", "interfaces": [...], "events": [...], "status": "success", "warnings": [...] }`.
   - If issues: `{ "status": "error", "error": "Reason (e.g., incompatible with v1.0)" }`.

### Few-Shot Examples (Cadence 1.0)
**Example 1: Complete NFT Contract with Correct Minter Pattern** (IMPORTANT: Never store contract references in resources)
```cadence
import NonFungibleToken from 0x1d7e57aa55817448
import MetadataViews from 0x1d7e57aa55817448
import ViewResolver from 0x1d7e57aa55817448

access(all) contract SimpleNFT: NonFungibleToken {
    access(all) var totalSupply: UInt64  // Use 'var' for mutable fields

    access(all) resource NFT: NonFungibleToken.NFT {
        access(all) let id: UInt64
        
        init(id: UInt64) {
            self.id = id
        }
        
        access(all) view fun getViews(): [Type] {
            return []
        }
        
        access(all) fun resolveView(_ view: Type): AnyStruct? {
            return nil
        }
    }

    // CORRECT: Minter accesses contract fields directly
    access(all) resource NFTMinter {
        access(all) fun mintNFT(
            recipient: &{NonFungibleToken.CollectionPublic},
            metadata: {String: String}
        ): UInt64 {
            // Access contract fields directly via contract name
            let newNFT <- create NFT(
                id: SimpleNFT.totalSupply  // Direct access, no stored reference
            )
            
            let mintedID = newNFT.id
            recipient.deposit(token: <-newNFT)
            
            // Update contract state directly
            SimpleNFT.totalSupply = SimpleNFT.totalSupply + 1
            
            return mintedID
        }
    }

    access(all) resource Collection: NonFungibleToken.Collection {
        access(all) var ownedNFTs: @{UInt64: NonFungibleToken.NFT}

        access(NonFungibleToken.Withdraw) fun withdraw(withdrawID: UInt64): @NonFungibleToken.NFT {
            let token <- self.ownedNFTs.remove(key: withdrawID) 
                ?? panic("missing NFT")
            return <-token
        }

        access(all) fun deposit(token: @NonFungibleToken.NFT) {
            let oldToken <- self.ownedNFTs[token.id] <- token
            destroy oldToken
        }

        access(all) view fun getIDs(): [UInt64] {
            return self.ownedNFTs.keys
        }

        access(all) view fun borrowNFT(_ id: UInt64): &NonFungibleToken.NFT? {
            return &self.ownedNFTs[id] as &NonFungibleToken.NFT?
        }

        init() {
            self.ownedNFTs <- {}
        }
    }

    access(all) fun createEmptyCollection(): @NonFungibleToken.Collection {
        return <- create Collection()
    }

    init() {
        self.totalSupply = 0
        self.account.storage.save(<-create NFTMinter(), to: /storage/NFTMinter)
        self.account.storage.save(<-create Collection(), to: /storage/Collection)
        
        let collectionCap = self.account.capabilities.storage.issue<&Collection>(/storage/Collection)
        self.account.capabilities.publish(collectionCap, at: /public/Collection)
    }
}

// WRONG: Never do this - storing contract references is not allowed
// access(all) resource BadMinter {
//     access(all) let contract: &SimpleNFT  // ❌ This causes compilation errors
//     init(contract: &SimpleNFT) {
//         self.contract = contract  // ❌ Cannot store contract references
//     }
// }
```

Generate contracts that are deployable via Flowzmith's CLI/API (e.g., `src/cli/contract_creator.py`). If requirements are ambiguous, ask for clarification in output. Prioritize safety, composability, and Flow best practices.""",
            variables=[],
            description="Detailed template for generating Cadence 1.0 compliant smart contracts with full migration guide adherence"
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