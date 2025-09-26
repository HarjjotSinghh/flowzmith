"""
Contract creation functionality for the CLI.

Handles step-by-step contract creation with various input methods.
"""

import os
import uuid
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from .api_client import APIClient
from .file_generators import FlowFileGenerator
from ..models.database import get_db
from ..models.generated_contract import GeneratedContract, ContractType, NetworkType, GenerationMethod

console = Console()

class ContractCreator:
    """Handles smart contract creation process."""

    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.file_generator = FlowFileGenerator()

    async def create_contract_interactive(self) -> Dict[str, Any]:
        """Guide user through interactive contract creation with automatic context loading."""
        console.print("🚀 Smart Contract Creation", style="bold blue")
        console.print("Creating your smart contract with AI assistance using available documentation context.", style="dim")

        # Automatically load context from /context/ directory
        console.print("📚 Loading documentation context...", style="blue")
        context_files = await self._load_default_context()
        
        if context_files:
            console.print(f"✅ Loaded {len(context_files)} context files for AI assistance", style="green")
            for file_info in context_files:
                console.print(f"  📄 {file_info['filename']} ({len(file_info['content'])} characters)", style="dim")
        else:
            console.print("⚠️  No context files found. Proceeding with basic generation.", style="yellow")

        # Step 1: Get contract requirements (enhanced for context-aware generation)
        requirements = await self._get_enhanced_contract_requirements()

        # Step 2: Generate contract using context and AI
        console.print("\n🤖 Generating contract with AI assistance...", style="blue")
        context_data = {
            "markdown_files": context_files,
            "requirements": requirements,
            "generation_mode": "markdown_context"
        }
        contract_content = await self._generate_contract_from_context(context_data)

        # Step 3: Review and confirm
        if await self._review_contract(requirements, contract_content):
            return await self._submit_contract(requirements, contract_content, "markdown_context")
        else:
            console.print("❌ Contract creation cancelled", style="yellow")
            return {"status": "cancelled"}

    async def _select_input_method(self) -> str:
        """Let user select contract input method."""
        console.print("\n📝 How would you like to create your smart contract?", style="blue")

        methods = [
            ("1", "Natural Language Description", "Describe your contract in plain English"),
            ("2", "Upload CADENCE (.cdc) File", "Provide existing Flow contract file"),
            ("3", "Upload Solidity (.sol) File", "Provide Solidity file for conversion"),
            ("4", "Paste Contract Code Directly", "Type or paste contract code"),
            ("5", "Use Template/Example", "Start from pre-built template"),
            ("6", "Markdown Context + AI Generation", "Provide markdown docs for AI to learn from")
        ]

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Option", style="cyan", width=10)
        table.add_column("Method", style="green")
        table.add_column("Description", style="white")

        for option, method, description in methods:
            table.add_row(option, method, description)

        console.print(table)

        choice = Prompt.ask(
            "\nSelect an option",
            choices=["1", "2", "3", "4", "5", "6"],
            default="1"
        )

        method_map = {
            "1": "natural_language",
            "2": "cadence_file",
            "3": "solidity_file",
            "4": "direct_code",
            "5": "template",
            "6": "markdown_context"
        }

        return method_map[choice]

    async def _get_contract_requirements(self) -> Dict[str, Any]:
        """Get contract requirements from user input."""
        console.print("\n🎯 Let's define your contract requirements:", style="blue")

        requirements = {
            "contract_name": Prompt.ask(
                "Contract name",
                default="MyToken" if Prompt.ask("Contract type", choices=["Token", "NFT", "Custom"], default="Token") == "Token" else "MyContract"
            ),
            "contract_type": Prompt.ask(
                "Contract type",
                choices=["Token", "NFT", "Marketplace", "DAO", "Custom"],
                default="Token"
            ),
            "description": Prompt.ask(
                "Brief description",
                default="A smart contract for managing digital assets"
            ),
            "network": Prompt.ask(
                "Target network",
                choices=["testnet", "mainnet"],
                default="testnet"
            )
        }

        # Additional requirements based on contract type
        if requirements["contract_type"] == "Token":
            requirements["token_details"] = {
                "initial_supply": Prompt.ask("Initial supply", default="1000.0"),
                "token_name": Prompt.ask("Token name", default="My Token"),
                "token_symbol": Prompt.ask("Token symbol", default="MTK"),
                "decimals": Prompt.ask("Decimals", default="8")
            }
        elif requirements["contract_type"] == "NFT":
            requirements["nft_details"] = {
                "collection_name": Prompt.ask("Collection name", default="My Collection"),
                "max_supply": Prompt.ask("Maximum supply (0 for unlimited)", default="0"),
                "royalty_fee": Prompt.ask("Royalty fee (%)", default="2.5")
            }

        return requirements

    async def _get_contract_content(self, input_method: str) -> str:
        """Get contract content based on selected input method."""
        if input_method == "natural_language":
            return await self._get_natural_language_input()
        elif input_method == "cadence_file":
            return await self._get_file_input(".cdc")
        elif input_method == "solidity_file":
            return await self._get_file_input(".sol")
        elif input_method == "direct_code":
            return await self._get_direct_code_input()
        elif input_method == "template":
            return await self._get_template_selection()
        elif input_method == "markdown_context":
            return await self._get_markdown_context_input()
        else:
            raise Exception(f"Unknown input method: {input_method}")

    async def _get_natural_language_input(self) -> str:
        """Get natural language description of contract requirements."""
        console.print("\n📄 Describe your smart contract in natural language:", style="blue")
        console.print("Example: 'I want to create an NFT contract with minting capabilities and metadata storage'", style="dim")

        description = Prompt.ask("\nContract requirements", multiline=True)
        return description.strip()

    async def _get_file_input(self, file_extension: str) -> str:
        """Get contract code from file upload."""
        console.print(f"\n📁 Please provide the path to your {file_extension} file:", style="blue")

        while True:
            file_path = Prompt.ask("File path")
            path = Path(file_path)

            if not path.exists():
                console.print(f"❌ File not found: {file_path}", style="red")
                continue

            if not path.suffix.lower() == file_extension:
                console.print(f"❌ File must be a {file_extension} file", style="red")
                continue

            try:
                content = path.read_text(encoding='utf-8')
                console.print(f"✅ Loaded {len(content)} characters from {file_path}", style="green")

                # Upload file to server
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Uploading file...", total=None)

                    try:
                        upload_result = await self.api_client.upload_file(path, file_extension.replace(".", ""))
                        progress.update(task, description="File uploaded successfully")
                        console.print(f"✅ File uploaded: {upload_result.get('file_id', 'unknown')}", style="green")
                    except Exception as e:
                        progress.update(task, description=f"Upload failed: {e}")
                        console.print(f"⚠️  File upload failed, but we'll continue with local content: {e}", style="yellow")

                return content

            except Exception as e:
                console.print(f"❌ Error reading file: {e}", style="red")

    async def _get_direct_code_input(self) -> str:
        """Get contract code directly from user input."""
        console.print("\n💻 Paste your contract code:", style="blue")
        console.print("Press Enter twice to finish input", style="dim")

        lines = []
        while True:
            line = Prompt.ask("")
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)

        code = "\n".join(lines[:-1])
        console.print(f"✅ Received {len(code)} characters of code", style="green")
        return code

    async def _get_template_selection(self) -> str:
        """Let user select from available contract templates."""
        templates = {
            "1": {
                "name": "Fungible Token",
                "description": "Basic Flow token contract with minting and transferring",
                "code": """
// Simple Fungible Token Contract
pub contract SimpleToken {
    pub var totalSupply: UFix64
    pub var balance: {Address: UFix64}

    init() {
        self.totalSupply = 1000.0
        self.balance = {}
        self.balance[self.account.address] = self.totalSupply
    }

    pub fun balanceOf(address: Address): UFix64 {
        return self.balance[address] ?? 0.0
    }

    pub fun transfer(from: Address, to: Address, amount: UFix64) {
        pre {
            self.balance[from] >= amount:
                "Insufficient balance"
        }

        self.balance[from] = self.balance[from]! - amount
        self.balance[to] = (self.balance[to] ?? 0.0) + amount
    }
}
                """
            },
            "2": {
                "name": "NFT Collection",
                "description": "Non-Fungible Token collection with metadata",
                "code": """
// NFT Collection Contract
pub contract NFTCollection {
    pub var totalSupply: UInt64
    pub var metadata: {UInt64: String}

    pub resource NFT {
        pub let id: UInt64
        pub let metadata: String

        init(id: UInt64, metadata: String) {
            self.id = id
            self.metadata = metadata
        }
    }

    init() {
        self.totalSupply = 0
        self.metadata = {}
    }

    pub fun mintNFT(metadata: String): @NFT {
        self.totalSupply = self.totalSupply + 1
        self.metadata[self.totalSupply] = metadata
        return <-create NFT(id: self.totalSupply, metadata: metadata)
    }
}
                """
            },
            "3": {
                "name": "Marketplace",
                "description": "Simple NFT marketplace with buying and selling",
                "code": """
// NFT Marketplace Contract
pub contract NFTMarketplace {
    pub var listings: {UInt64: Listing}

    pub struct Listing {
        pub let nftID: UInt64
        pub let price: UFix64
        pub let seller: Address

        init(nftID: UInt64, price: UFix64, seller: Address) {
            self.nftID = nftID
            self.price = price
            self.seller = seller
        }
    }

    init() {
        self.listings = {}
    }

    pub fun listNFT(nftID: UInt64, price: UFix64, seller: Address) {
        self.listings[nftID] = Listing(nftID: nftID, price: price, seller: seller)
    }

    pub fun buyNFT(nftID: UInt64, buyer: Address) {
        let listing = self.listings[nftID] ?? panic("NFT not listed")
        // Transfer logic would go here
        self.listings.remove(key: nftID)
    }
}
                """
            }
        }

        console.print("\n📋 Select a contract template:", style="blue")

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Option", style="cyan", width=10)
        table.add_column("Name", style="green")
        table.add_column("Description", style="white")

        for key, template in templates.items():
            table.add_row(key, template["name"], template["description"])

        console.print(table)

        choice = Prompt.ask("Select template", choices=list(templates.keys()))
        return templates[choice]["code"]

    async def _get_markdown_context_input(self) -> str:
        """Get contract requirements using markdown context files."""
        console.print("\n📚 Markdown Context + AI Generation", style="blue")
        console.print("This mode uses your markdown documentation to generate smart contracts.", style="dim")

        # Step 1: Get markdown files
        markdown_files = await self._get_markdown_files()

        # Step 2: Get contract requirements
        contract_requirements = await self._get_enhanced_contract_requirements()

        # Step 3: Combine context and requirements
        context_data = {
            "markdown_files": markdown_files,
            "requirements": contract_requirements,
            "generation_mode": "markdown_context"
        }

        return await self._generate_contract_from_context(context_data)

    async def _get_markdown_files(self) -> List[Dict[str, str]]:
        """Get markdown files for context."""
        console.print("\n📁 Provide markdown documentation files:", style="blue")
        console.print("These files will be used as context for AI contract generation.", style="dim")

        files = []

        while True:
            file_path = Prompt.ask("Enter markdown file path (or leave empty to finish)")

            if not file_path.strip():
                break

            path = Path(file_path)

            if not path.exists():
                console.print(f"❌ File not found: {file_path}", style="red")
                continue

            if not path.suffix.lower() in ['.md', '.markdown']:
                console.print(f"❌ File must be a markdown file (.md or .markdown)", style="red")
                continue

            try:
                content = path.read_text(encoding='utf-8')
                files.append({
                    "filename": path.name,
                    "content": content,
                    "path": str(path)
                })
                console.print(f"✅ Loaded: {path.name} ({len(content)} characters)", style="green")
            except Exception as e:
                console.print(f"❌ Error reading file: {e}", style="red")

        if not files:
            console.print("❌ No markdown files provided. Using default context.", style="yellow")
            # Load default context files
            default_context_path = Path(__file__).parent.parent.parent / "context"
            if default_context_path.exists():
                for md_file in default_context_path.glob("*.md"):
                    try:
                        content = md_file.read_text(encoding='utf-8')
                        files.append({
                            "filename": md_file.name,
                            "content": content,
                            "path": str(md_file)
                        })
                        console.print(f"📄 Added default context: {md_file.name}", style="dim")
                    except Exception as e:
                        console.print(f"⚠️  Could not load default context {md_file.name}: {e}", style="yellow")

        return files

    async def _load_default_context(self) -> List[Dict[str, str]]:
        """Automatically load all markdown files from the /context/ directory."""
        files = []
        
        # Get the context directory path
        context_path = Path(__file__).parent.parent.parent / "context"
        
        if not context_path.exists():
            console.print(f"⚠️  Context directory not found: {context_path}", style="yellow")
            return files
        
        # Recursively find all markdown files in context directory and subdirectories
        markdown_patterns = ["*.md", "*.markdown"]
        
        for pattern in markdown_patterns:
            for md_file in context_path.rglob(pattern):
                try:
                    content = md_file.read_text(encoding='utf-8', errors='ignore')
                    # Get relative path from context directory for better organization
                    relative_path = md_file.relative_to(context_path)
                    files.append({
                        "filename": md_file.name,
                        "content": content,
                        "path": str(md_file),
                        "relative_path": str(relative_path)
                    })
                except Exception as e:
                    console.print(f"⚠️  Could not load context file {md_file.name}: {e}", style="yellow")
        
        # Sort files by relative path for consistent ordering
        files.sort(key=lambda x: x.get("relative_path", x["filename"]))
        
        return files

    async def _get_enhanced_contract_requirements(self) -> Dict[str, Any]:
        """Get enhanced contract requirements with Flow-specific details."""
        console.print("\n🎯 Define your Flow smart contract requirements:", style="blue")

        requirements = {
            "contract_name": Prompt.ask("Contract name", default="MyFlowContract"),
            "contract_type": Prompt.ask(
                "Contract type",
                choices=["Token", "NFT", "Marketplace", "DAO", "Vesting", "Custom"],
                default="Token"
            ),
            "description": Prompt.ask(
                "Brief description",
                default="A Flow blockchain smart contract"
            ),
            "network": Prompt.ask(
                "Target network",
                choices=["emulator", "testnet", "mainnet"],
                default="testnet"
            ),
            "account_setup": Prompt.ask(
                "Account setup",
                choices=["single", "multi", "proxy"],
                default="single"
            )
        }

        # Flow-specific requirements
        if requirements["contract_type"] == "Token":
            requirements["token_details"] = {
                "initial_supply": Prompt.ask("Initial supply", default="1000.0"),
                "token_name": Prompt.ask("Token name", default="My Token"),
                "token_symbol": Prompt.ask("Token symbol", default="MTK"),
                "decimals": Prompt.ask("Decimals", default="8"),
                "vault_type": Prompt.ask("Vault type", choices=["standard", "custom"], default="standard")
            }
        elif requirements["contract_type"] == "NFT":
            requirements["nft_details"] = {
                "collection_name": Prompt.ask("Collection name", default="My Collection"),
                "max_supply": Prompt.ask("Maximum supply (0 for unlimited)", default="0"),
                "royalty_fee": Prompt.ask("Royalty fee (%)", default="2.5"),
                "metadata_storage": Prompt.ask("Metadata storage", choices=["onchain", "offchain"], default="onchain")
            }

        # Additional Flow features
        console.print("\n🔧 Additional Flow features:", style="cyan")
        requirements["features"] = []

        if Confirm.ask("Include transaction scripts?"):
            requirements["features"].append("transaction_scripts")

        if Confirm.ask("Include deployment scripts?"):
            requirements["features"].append("deployment_scripts")

        if Confirm.ask("Include test cases?"):
            requirements["features"].append("test_cases")

        return requirements

    async def _generate_contract_from_context(self, context_data: Dict[str, Any]) -> str:
        """Generate contract from markdown context using AI."""
        console.print("\n🤖 Generating smart contract from context...", style="blue")

        # Prepare the prompt with context
        prompt = self._build_context_aware_prompt(context_data)

        try:
            # Submit to API for generation
            # Build plain-text requirements and aggregated context to match server schema
            req = context_data["requirements"]
            requirements_text = (
                f"Name: {req.get('contract_name', '')}\n"
                f"Type: {req.get('contract_type', '')}\n"
                f"Description: {req.get('description', '')}\n"
                f"Network: {req.get('network', '')}\n"
                f"Account Setup: {req.get('account_setup', '')}\n"
            )
            # Include additional details based on type
            if req.get("contract_type") == "Token" and isinstance(req.get("token_details"), dict):
                td = req["token_details"]
                requirements_text += (
                    "Token Details:\n"
                    f"  - Initial Supply: {td.get('initial_supply', '')}\n"
                    f"  - Token Name: {td.get('token_name', '')}\n"
                    f"  - Token Symbol: {td.get('token_symbol', '')}\n"
                    f"  - Decimals: {td.get('decimals', '')}\n"
                    f"  - Vault Type: {td.get('vault_type', '')}\n"
                )
            elif req.get("contract_type") == "NFT" and isinstance(req.get("nft_details"), dict):
                nd = req["nft_details"]
                requirements_text += (
                    "NFT Details:\n"
                    f"  - Collection Name: {nd.get('collection_name', '')}\n"
                    f"  - Max Supply: {nd.get('max_supply', '')}\n"
                    f"  - Royalty Fee: {nd.get('royalty_fee', '')}%\n"
                    f"  - Metadata Storage: {nd.get('metadata_storage', '')}\n"
                )
            # Include selected features
            features = req.get("features", [])
            if features:
                requirements_text += "Features:\n" + "\n".join([f"  - {f}" for f in features]) + "\n"

            # Aggregate markdown context into a single string
            context_text_parts = []
            for i, md in enumerate(context_data.get("markdown_files", [])):
                fname = md.get("filename", f"context_{i+1}.md")
                content = md.get("content", "")
                context_text_parts.append(f"\n### {fname}\n\n{content}\n")
            context_text = "".join(context_text_parts)

            generation_request = {
                "requirements": requirements_text.strip(),
                "context": context_text,
                "pre_conditions": req.get("pre_conditions"),
                "post_conditions": req.get("post_conditions"),
                "network": req.get("network", "emulator"),
            }

            # Use streaming generation for real-time output
            console.print("🔄 Starting real-time contract generation...", style="cyan")
            
            generated_content = ""
            
            # Stream chunks with real-time display
            async for chunk in self.api_client.stream_generate_contract_with_context(generation_request):
                if chunk.get("type") == "content":
                    content = chunk.get("chunk", "")
                    generated_content += content
                    # Write content to stdout in real-time without extra newlines and flush immediately
                    sys.stdout.write(content)
                    sys.stdout.flush()
                elif chunk.get("type") == "status":
                    status = chunk.get("data", {})
                    if status.get("stage"):
                        console.print(f"\n📌 {status['stage']}", style="blue")
                elif chunk.get("type") == "progress":
                    progress_data = chunk.get("data", {})
                    if progress_data.get("message"):
                        console.print(f"⚡ {progress_data['message']}", style="cyan")
                elif chunk.get("type") == "complete":
                    final_data = chunk.get("data", {})
                    console.print(f"\n✅ Generation complete! Generated {len(generated_content)} characters", style="green")
                    if final_data.get("submission_id"):
                        console.print(f"📄 Submission ID: {final_data['submission_id']}", style="dim")
                    break
                elif chunk.get("type") == "error":
                    error_msg = chunk.get("error", "Unknown error")
                    console.print(f"\n❌ Generation failed: {error_msg}", style="red")
                    raise Exception(f"Contract generation failed: {error_msg}")
                
            return generated_content

        except Exception as e:
            console.print(f"\n❌ Error during streaming generation: {e}", style="red")
            console.print("🔄 Falling back to non-streaming generation...", style="yellow")
            
            # Fallback to regular generation
            try:
                result = await self.api_client.generate_contract_with_context(generation_request)
                
                if result.get("status") == "success":
                    generated_content = result.get("content", "")
                    console.print(f"✅ Generated contract with {len(generated_content)} characters", style="green")
                    return generated_content
                else:
                    console.print(f"❌ Generation failed: {result.get('error', 'Unknown error')}", style="red")
                    raise Exception(f"Contract generation failed: {result.get('error')}")
                    
            except Exception as fallback_e:
                console.print(f"❌ Fallback generation also failed: {fallback_e}", style="red")
                # Final fallback to basic generation
                return await self._fallback_generation(context_data["requirements"])

    def _build_context_aware_prompt(self, context_data: Dict[str, Any]) -> str:
        """Build a context-aware prompt for contract generation."""
        requirements = context_data["requirements"]

        prompt = f"""Generate a complete Flow blockchain smart contract based on the following context and requirements:

## Contract Requirements:
- Name: {requirements['contract_name']}
- Type: {requirements['contract_type']}
- Description: {requirements['description']}
- Network: {requirements['network']}
- Account Setup: {requirements['account_setup']}

## Additional Context Files:
"""

        # Add markdown context
        for i, md_file in enumerate(context_data["markdown_files"]):
            prompt += f"""
### Context File {i+1}: {md_file['filename']}
{md_file['content'][:1000]}...  # Truncated for brevity
"""

        # Add specific requirements
        if requirements["contract_type"] == "Token" and "token_details" in requirements:
            details = requirements["token_details"]
            prompt += f"""
## Token Details:
- Initial Supply: {details['initial_supply']}
- Token Name: {details['token_name']}
- Token Symbol: {details['token_symbol']}
- Decimals: {details['decimals']}
- Vault Type: {details['vault_type']}
"""

        # Generation instructions
        prompt += """
## Generation Requirements:
1. Generate a complete Cadence (.cdc) smart contract file
2. Include proper resource definitions, interfaces, and error handling
3. Follow Flow blockchain best practices
4. Include comprehensive documentation comments
5. Make the contract production-ready with proper access controls
6. Generate a complete flow.json configuration file
7. Include deployment scripts if requested
8. Include transaction scripts if requested
9. Include test cases if requested

## Output Format:
Provide the complete smart contract code and all necessary configuration files in a structured format that can be directly deployed to the Flow blockchain.
"""

        return prompt

    async def _fallback_generation(self, requirements: Dict[str, Any]) -> str:
        """Fallback generation when context-based generation fails."""
        console.print("🔄 Using fallback generation mode...", style="yellow")

        # Simple template based on requirements
        if requirements["contract_type"] == "Token":
            return self._generate_token_contract_template(requirements)
        elif requirements["contract_type"] == "NFT":
            return self._generate_nft_contract_template(requirements)
        else:
            return self._generate_generic_contract_template(requirements)

    def _generate_token_contract_template(self, requirements: Dict[str, Any]) -> str:
        """Generate a basic token contract template."""
        token_details = requirements.get("token_details", {})

        contract = f'''// {requirements['contract_name']} - Generated Smart Contract
// Contract Type: {requirements['contract_type']}
// Network: {requirements['network']}

pub contract {requirements['contract_name']} {{

    // Events
    pub event TokensMinted(amount: UFix64, recipient: Address)
    pub event TokensTransferred(from: Address, to: Address, amount: UFix64)
    pub event TokensBurned(amount: UFix64, burner: Address)

    // Contract state
    pub var totalSupply: UFix64
    pub let name: String
    pub let symbol: String
    pub var decimals: UInt8

    // Vault resource
    pub resource Vault {{
        pub var balance: UFix64

        init(balance: UFix64) {{
            self.balance = balance
        }}

        pub fun withdraw(amount: UFix64): @Vault {{
            self.balance = self.balance - amount
            return <-create Vault(balance: amount)
        }}

        pub fun deposit(from: @Vault) {{
            self.balance = self.balance + from.balance
            destroy from
        }}

        destroy() {{
            {requirements['contract_name']}.totalSupply = {requirements['contract_name']}.totalSupply - self.balance
            emit TokensBurned(amount: self.balance, burner: self.owner?.address!)
        }}
    }}

    // Receiver interface
    pub resource interface Receiver {{
        pub fun deposit(from: @Vault)
    }}

    // Provider interface
    pub resource interface Provider {{
        pub fun withdraw(amount: UFix64): @Vault
        pub fun balance: UFix64
    }}

    // Functions
    init() {{
        self.totalSupply = {token_details.get('initial_supply', '1000.0')}
        self.name = "{token_details.get('token_name', 'My Token')}"
        self.symbol = "{token_details.get('token_symbol', 'MTK')}"
        self.decimals = {token_details.get('decimals', '8')}

        // Create initial vault for contract creator
        let vault <- create Vault(balance: self.totalSupply)
        self.account.save(<-vault, to: /storage/MainVault)
        self.account.link<&Vault>(/public/MainVault, target: /storage/MainVault)

        emit TokensMinted(amount: self.totalSupply, recipient: self.account.address)
    }}
}}
'''
        return contract

    def _generate_nft_contract_template(self, requirements: Dict[str, Any]) -> str:
        """Generate a basic NFT contract template."""
        nft_details = requirements.get("nft_details", {})

        contract = f'''// {requirements['contract_name']} - Generated Smart Contract
// Contract Type: {requirements['contract_type']}
// Network: {requirements['network']}

pub contract {requirements['contract_name']} {{

    // Events
    pub event NFTMinted(id: UInt64, metadata: String, recipient: Address)
    pub event NFTTransferred(from: Address, to: Address, id: UInt64)

    // Contract state
    pub var totalSupply: UInt64
    pub let collectionName: String

    // NFT resource
    pub resource NFT: NFTStandard.NFT {{
        pub let id: UInt64
        pub let metadata: String

        init(id: UInt64, metadata: String) {{
            self.id = id
            self.metadata = metadata
        }}
    }}

    // Collection resource
    pub resource Collection {{
        pub var ownedNFTs: @{{UInt64: NFT}}

        init() {{
            self.ownedNFTs <- {{}}
        }}

        pub fun deposit(token: @NFT) {{
            let id = token.id
            self.ownedNFTs[id] <-! token
        }}

        pub fun withdraw(id: UInt64): @NFT {{
            let token <- self.ownedNFTs.remove(key: id)!
            return <-token
        }}

        pub fun getIDs(): [UInt64] {{
            return self.ownedNFTs.keys
        }}

        destroy() {{
            destroy self.ownedNFTs
        }}
    }}

    // Public functions
    pub fun mintNFT(metadata: String): @NFT {{
        self.totalSupply = self.totalSupply + 1
        let newNFT <- create NFT(id: self.totalSupply, metadata: metadata)
        emit NFTMinted(id: self.totalSupply, metadata: metadata, recipient: self.account.address)
        return <-newNFT
    }}

    init() {{
        self.totalSupply = 0
        self.collectionName = "{nft_details.get('collection_name', 'My Collection')}"

        // Create collection for contract creator
        self.account.save(<-create Collection(), to: /storage/NFTCollection)
        self.account.link<&Collection>(/public/NFTCollection, target: /storage/NFTCollection)
    }}
}}
'''
        return contract

    def _generate_generic_contract_template(self, requirements: Dict[str, Any]) -> str:
        """Generate a generic contract template."""
        contract = f'''// {requirements['contract_name']} - Generated Smart Contract
// Contract Type: {requirements['contract_type']}
// Network: {requirements['network']}

pub contract {requirements['contract_name']} {{

    // Events
    pub event ContractInitialized()

    // Contract state
    pub let contractOwner: Address

    // Resources and functions will be added based on your specific requirements
    // This is a template that needs to be customized

    init() {{
        self.contractOwner = self.account.address
        emit ContractInitialized()
    }}
}}
'''
        return contract

    async def _review_contract(self, requirements: Dict[str, Any], contract_content: str) -> bool:
        """Show contract summary and ask for confirmation."""
        console.print("\n📊 Contract Summary:", style="blue")

        summary_table = Table(show_header=False, box=None)
        summary_table.add_column("Property", style="cyan")
        summary_table.add_column("Value", style="white")

        summary_table.add_row("Name", requirements["contract_name"])
        summary_table.add_row("Type", requirements["contract_type"])
        summary_table.add_row("Network", requirements["network"])
        summary_table.add_row("Description", requirements["description"])
        summary_table.add_row("Content Length", f"{len(contract_content)} characters")

        console.print(summary_table)

        # Show code preview
        if len(contract_content) > 200:
            preview = contract_content[:200] + "..."
        else:
            preview = contract_content

        console.print("\n💻 Code Preview:", style="blue")
        console.print(Panel(preview, title="Contract Code", border_style="green"))

        return Confirm.ask("\nProceed with contract creation?")

    async def _submit_contract(self, requirements: Dict[str, Any], contract_content: str, input_method: str) -> Dict[str, Any]:
        """Submit contract to API."""
        console.print("\n🚀 Creating contract...", style="blue")

        # Track generation start time
        generation_start_time = time.time()

        # Prepare contract data
        contract_data = {
            "contract_name": requirements["contract_name"],
            "contract_type": requirements["contract_type"],
            "description": requirements["description"],
            "network": requirements["network"],
            "input_method": input_method,
            "content": contract_content,
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "cli_generated": True
            }
        }

        # Add type-specific metadata
        if requirements["contract_type"] == "Token" and "token_details" in requirements:
            contract_data["metadata"]["token_details"] = requirements["token_details"]
        elif requirements["contract_type"] == "NFT" and "nft_details" in requirements:
            contract_data["metadata"]["nft_details"] = requirements["nft_details"]

        # Add Flow project generation requirements
        if input_method == "markdown_context" or "features" in requirements:
            contract_data["generate_flow_project"] = True
            contract_data["flow_config"] = {
                "network": requirements["network"],
                "account_setup": requirements.get("account_setup", "single"),
                "features": requirements.get("features", []),
                "include_flow_json": True
            }

        # Connect to WebSocket for real-time updates
        try:
            connection_id = await self.api_client.connect_websocket()
            console.print(f"✅ Connected to real-time updates (ID: {connection_id})", style="green")
        except Exception as e:
            console.print(f"⚠️  WebSocket connection failed: {e}", style="yellow")
            console.print("Continuing without real-time updates...", style="dim")

        # Submit contract with progress tracking
        result = await self._submit_with_progress(contract_data)

        # Calculate generation time
        generation_time = time.time() - generation_start_time

        # Always save contract to flow_projects directory and database
        await self._save_contract_to_filesystem(result, requirements, contract_content, input_method)
        await self._save_contract_to_database(result, requirements, contract_content, input_method, generation_time)

        # Handle Flow project output (for additional files)
        if result.get("status") == "success" and contract_data.get("generate_flow_project"):
            await self._handle_flow_project_output(result, requirements)

        return result

    async def _submit_with_progress(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit contract with real-time progress tracking."""
        operation_id = str(uuid.uuid4())

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Submitting contract...", total=100)

            try:
                # Submit contract
                result = await self.api_client.submit_contract(contract_data)
                progress.update(task, advance=25, description="Contract submitted")

                # Wait for processing (simulate for now)
                import time
                for i in range(3):
                    time.sleep(1)
                    progress.update(task, advance=25, description=f"Processing step {i+1}/3...")

                progress.update(task, completed=100, description="Contract submitted successfully!")

                console.print("\n✅ Contract submitted successfully!", style="green")
                console.print(f"Submission ID: {result.get('submission_id', 'unknown')}", style="cyan")
                console.print(f"Status: {result.get('status', 'processing')}", style="cyan")

                return result

            except Exception as e:
                progress.update(task, description=f"Error: {e}")
                console.print(f"\n❌ Contract creation failed: {e}", style="red")
                return {"status": "failed", "error": str(e)}

    async def _handle_flow_project_output(self, result: Dict[str, Any], requirements: Dict[str, Any]) -> None:
        """Handle and save Flow project output locally."""
        console.print("\n💾 Saving Flow project files...", style="blue")

        # Create project directory
        project_name = requirements["contract_name"]
        base_dir = Path("flow_projects")
        project_dir = base_dir / project_name

        try:
            project_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"📁 Created project directory: {project_dir}", style="green")
        except Exception as e:
            console.print(f"❌ Failed to create project directory: {e}", style="red")
            return

        # Extract and save generated files
        generated_files = result.get("generated_files", {})

        # Save main contract file
        if "contract_cdc" in generated_files:
            contract_file = project_dir / f"{requirements['contract_name']}.cdc"
            try:
                contract_file.write_text(generated_files["contract_cdc"], encoding='utf-8')
                console.print(f"✅ Saved contract: {contract_file}", style="green")
            except Exception as e:
                console.print(f"❌ Failed to save contract file: {e}", style="red")

        # Save flow.json
        if "flow_json" in generated_files:
            flow_json_file = project_dir / "flow.json"
            try:
                import json
                flow_json_file.write_text(json.dumps(generated_files["flow_json"], indent=2), encoding='utf-8')
                console.print(f"✅ Saved flow.json: {flow_json_file}", style="green")
            except Exception as e:
                console.print(f"❌ Failed to save flow.json: {e}", style="red")

        # Save additional files based on features
        if "transaction_scripts" in generated_files:
            tx_dir = project_dir / "transactions"
            tx_dir.mkdir(exist_ok=True)
            for script_name, script_content in generated_files["transaction_scripts"].items():
                script_file = tx_dir / f"{script_name}.cdc"
                try:
                    script_file.write_text(script_content, encoding='utf-8')
                    console.print(f"✅ Saved transaction script: {script_file}", style="green")
                except Exception as e:
                    console.print(f"❌ Failed to save transaction script {script_name}: {e}", style="red")

        if "deployment_scripts" in generated_files:
            deploy_dir = project_dir / "scripts"
            deploy_dir.mkdir(exist_ok=True)
            for script_name, script_content in generated_files["deployment_scripts"].items():
                script_file = deploy_dir / f"{script_name}.cdc"
                try:
                    script_file.write_text(script_content, encoding='utf-8')
                    console.print(f"✅ Saved deployment script: {script_file}", style="green")
                except Exception as e:
                    console.print(f"❌ Failed to save deployment script {script_name}: {e}", style="red")

        if "test_cases" in generated_files:
            test_dir = project_dir / "tests"
            test_dir.mkdir(exist_ok=True)
            for test_name, test_content in generated_files["test_cases"].items():
                test_file = test_dir / f"{test_name}.cdc"
                try:
                    test_file.write_text(test_content, encoding='utf-8')
                    console.print(f"✅ Saved test case: {test_file}", style="green")
                except Exception as e:
                    console.print(f"❌ Failed to save test case {test_name}: {e}", style="red")

        # Create README file
        readme_content = self._generate_readme_content(requirements, generated_files)
        readme_file = project_dir / "README.md"
        try:
            readme_file.write_text(readme_content, encoding='utf-8')
            console.print(f"✅ Saved README: {readme_file}", style="green")
        except Exception as e:
            console.print(f"❌ Failed to save README: {e}", style="red")

        # Display project summary
        console.print("\n📊 Flow Project Summary:", style="blue")
        summary_table = Table(show_header=False, box=None)
        summary_table.add_column("Item", style="cyan")
        summary_table.add_column("Value", style="white")

        summary_table.add_row("Project Directory", str(project_dir))
        summary_table.add_row("Contract Name", requirements["contract_name"])
        summary_table.add_row("Network", requirements["network"])
        summary_table.add_row("Files Generated", str(len(generated_files)))

        console.print(summary_table)

        # Show next steps
        console.print("\n🚀 Next Steps:", style="green")
        console.print("1. Navigate to project directory:", style="white")
        console.print(f"   cd {project_dir}", style="cyan")
        console.print("2. Install dependencies:", style="white")
        console.print("   flow dependencies install", style="cyan")
        console.print("3. Deploy to network:", style="white")
        console.print("   flow project deploy", style="cyan")

    def _generate_readme_content(self, requirements: Dict[str, Any], generated_files: Dict[str, Any]) -> str:
        """Generate README content for the Flow project."""
        readme = f"""# {requirements['contract_name']}

{requirements['description']}

## Project Overview
- **Contract Type**: {requirements['contract_type']}
- **Target Network**: {requirements['network']}
- **Generated**: Smart Contract LLM Builder CLI

## Project Structure
```
{requirements['contract_name']}/
├── {requirements['contract_name']}.cdc      # Main smart contract
├── flow.json                              # Flow project configuration
"""

        if "transaction_scripts" in generated_files:
            readme += "├── transactions/                          # Transaction scripts\n"
        if "deployment_scripts" in generated_files:
            readme += "├── scripts/                               # Deployment scripts\n"
        if "test_cases" in generated_files:
            readme += "├── tests/                                 # Test cases\n"

        readme += """└── README.md                              # This file
```

## Setup Instructions

1. **Install Flow CLI**
   ```bash
   sh -ci "$(curl -fsSL https://storage.googleapis.com/flow-cli/install.sh)"
   ```

2. **Navigate to Project**
   ```bash
   cd {requirements['contract_name']}
   ```

3. **Install Dependencies**
   ```bash
   flow dependencies install
   ```

4. **Start Flow Emulator (for testing)**
   ```bash
   flow emulator start
   ```

5. **Deploy Contract**
   ```bash
   flow project deploy
   ```

## Features"""

        features = requirements.get("features", [])
        if "transaction_scripts" in features:
            readme += "\n- ✅ Transaction scripts included"
        if "deployment_scripts" in features:
            readme += "\n- ✅ Deployment scripts included"
        if "test_cases" in features:
            readme += "\n- ✅ Test cases included"

        readme += """

## Contract Details

This contract was generated using the Smart Contract LLM Builder CLI with markdown context and AI assistance.

### Generated Files:
"""

        for file_type, content in generated_files.items():
            if isinstance(content, dict):
                readme += f"- {file_type.replace('_', ' ').title()}: {len(content)} files\n"
            else:
                readme += f"- {file_type.replace('_', ' ').title()}: 1 file\n"

        readme += f"""
## Network Configuration

- **Target Network**: {requirements['network']}
- **Account Setup**: {requirements.get('account_setup', 'single')}

## Support

For issues or questions about this generated contract, please refer to the original documentation context used for generation or consult the Flow blockchain documentation.

---
Generated by Smart Contract LLM Builder CLI
"""
        return readme

    async def _save_contract_to_filesystem(self, result: Dict[str, Any], requirements: Dict[str, Any], 
                                         contract_content: str, input_method: str) -> str:
        """Save contract to flow_projects directory with all supporting files and return the project path."""
        try:
            # Create flow_projects directory if it doesn't exist
            flow_projects_dir = Path("flow_projects")
            flow_projects_dir.mkdir(exist_ok=True)
            
            # Generate unique project name using contract ID if available, otherwise timestamp
            contract_name = requirements.get("contract_name", requirements.get("name", "Contract"))
            contract_id = result.get("contract_id", str(uuid.uuid4()))
            project_dir = flow_projects_dir / contract_id
            project_dir.mkdir(exist_ok=True)
            
            # Create contracts directory
            contracts_dir = project_dir / "contracts"
            contracts_dir.mkdir(exist_ok=True)
            
            # Save main contract file in contracts directory
            contract_file = contracts_dir / f"{contract_name}.cdc"
            contract_file.write_text(contract_content, encoding='utf-8')
            console.print(f"✅ Saved contract: {contract_file}", style="green")
            
            # Get contract type for file generation
            contract_type = requirements.get("contract_type", requirements.get("type", "custom"))
            
            # Generate and save flow.json
            flow_json_content = self.file_generator.generate_flow_json(
                contract_name, 
                contract_type, 
                requirements.get("network", "testnet")
            )
            flow_json_file = project_dir / "flow.json"
            flow_json_file.write_text(json.dumps(flow_json_content, indent=2), encoding='utf-8')
            console.print(f"✅ Saved flow.json: {flow_json_file}", style="green")
            
            # Generate and save transactions
            transactions = self.file_generator.generate_transactions(contract_name, contract_type)
            if transactions:
                transactions_dir = project_dir / "transactions"
                transactions_dir.mkdir(exist_ok=True)
                for tx_name, tx_content in transactions.items():
                    tx_file = transactions_dir / f"{tx_name}.cdc"
                    tx_file.write_text(tx_content, encoding='utf-8')
                    console.print(f"✅ Saved transaction: {tx_file}", style="green")
            
            # Generate and save scripts
            scripts = self.file_generator.generate_scripts(contract_name, contract_type)
            if scripts:
                scripts_dir = project_dir / "scripts"
                scripts_dir.mkdir(exist_ok=True)
                for script_name, script_content in scripts.items():
                    script_file = scripts_dir / f"{script_name}.cdc"
                    script_file.write_text(script_content, encoding='utf-8')
                    console.print(f"✅ Saved script: {script_file}", style="green")
            
            # Generate and save tests
            tests = self.file_generator.generate_tests(contract_name, contract_type)
            if tests:
                tests_dir = project_dir / "tests"
                tests_dir.mkdir(exist_ok=True)
                for test_name, test_content in tests.items():
                    test_file = tests_dir / f"{test_name}.cdc"
                    test_file.write_text(test_content, encoding='utf-8')
                    console.print(f"✅ Saved test: {test_file}", style="green")
            
            # Save metadata file
            metadata = {
                "contract_id": contract_id,
                "contract_name": contract_name,
                "contract_type": contract_type,
                "network": requirements.get("network", "testnet"),
                "input_method": input_method,
                "requirements": requirements,
                "generated_at": datetime.now().isoformat(),
                "result": result,
                "files_generated": {
                    "contract": f"contracts/{contract_name}.cdc",
                    "flow_json": "flow.json",
                    "transactions": list(transactions.keys()) if transactions else [],
                    "scripts": list(scripts.keys()) if scripts else [],
                    "tests": list(tests.keys()) if tests else []
                }
            }
            
            metadata_file = project_dir / "metadata.json"
            metadata_file.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
            console.print(f"✅ Saved metadata: {metadata_file}", style="green")
            
            # Create comprehensive README
            readme_content = f"""# {contract_name}

Generated by Smart Contract LLM Builder

## Contract Details
- **ID**: {contract_id}
- **Name**: {contract_name}
- **Type**: {contract_type}
- **Network**: {requirements.get("network", "testnet")}
- **Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Input Method**: {input_method}

## Project Structure
```
{contract_id}/
├── contracts/
│   └── {contract_name}.cdc          # Main contract
├── transactions/                    # Transaction scripts
{chr(10).join([f"│   └── {tx}.cdc" for tx in (transactions.keys() if transactions else [])])}
├── scripts/                         # Query scripts  
{chr(10).join([f"│   └── {script}.cdc" for script in (scripts.keys() if scripts else [])])}
├── tests/                           # Test files
{chr(10).join([f"│   └── {test}.cdc" for test in (tests.keys() if tests else [])])}
├── flow.json                        # Flow configuration
├── metadata.json                    # Generation metadata
└── README.md                        # This file
```

## Description
{requirements.get("description", "No description provided")}

## Getting Started

1. **Install Flow CLI** (if not already installed):
   ```bash
   sh -ci "$(curl -fsSL https://raw.githubusercontent.com/onflow/flow-cli/master/install.sh)"
   ```

2. **Navigate to project directory**:
   ```bash
   cd {project_dir}
   ```

3. **Deploy to testnet**:
   ```bash
   flow project deploy --network testnet
   ```

4. **Run transactions** (example):
   ```bash
   flow transactions send ./transactions/setup_account.cdc --network testnet
   ```

5. **Execute scripts** (example):
   ```bash
   flow scripts execute ./scripts/get_balance.cdc --network testnet
   ```

## Files Generated

### Contract
- `contracts/{contract_name}.cdc` - Main smart contract

### Transactions
{chr(10).join([f"- `transactions/{tx}.cdc`" for tx in (transactions.keys() if transactions else ["None generated"])])}

### Scripts  
{chr(10).join([f"- `scripts/{script}.cdc`" for script in (scripts.keys() if scripts else ["None generated"])])}

### Tests
{chr(10).join([f"- `tests/{test}.cdc`" for test in (tests.keys() if tests else ["None generated"])])}

## Next Steps
1. Review and customize the generated files as needed
2. Update account addresses in flow.json
3. Add your private keys to flow.json (keep them secure!)
4. Test the contract on testnet before mainnet deployment
5. Consider adding more comprehensive tests

## Support
For more information about Flow and Cadence development, visit:
- [Flow Documentation](https://docs.onflow.org/)
- [Cadence Language Reference](https://docs.onflow.org/cadence/)
"""
            
            readme_file = project_dir / "README.md"
            readme_file.write_text(readme_content, encoding='utf-8')
            console.print(f"✅ Saved README: {readme_file}", style="green")
            
            # Display project summary
            console.print("\n📊 Flow Project Summary:", style="blue")
            summary_table = Table(show_header=False, box=None)
            summary_table.add_column("Item", style="cyan")
            summary_table.add_column("Value", style="white")

            summary_table.add_row("Project ID", contract_id)
            summary_table.add_row("Project Directory", str(project_dir))
            summary_table.add_row("Contract Name", contract_name)
            summary_table.add_row("Contract Type", contract_type)
            summary_table.add_row("Network", requirements.get("network", "testnet"))
            summary_table.add_row("Transactions", str(len(transactions)) if transactions else "0")
            summary_table.add_row("Scripts", str(len(scripts)) if scripts else "0")
            summary_table.add_row("Tests", str(len(tests)) if tests else "0")

            console.print(summary_table)
            
            console.print(f"\n✅ Complete Flow project saved to: {project_dir}", style="bold green")
            return str(project_dir)
            
        except Exception as e:
            console.print(f"❌ Failed to save contract to filesystem: {e}", style="red")
            import traceback
            console.print(f"Error details: {traceback.format_exc()}", style="red")
            return ""

    async def _save_contract_to_database(self, result: Dict[str, Any], requirements: Dict[str, Any], 
                                       contract_content: str, input_method: str, generation_time: float) -> None:
        """Save contract metadata to database."""
        try:
            # Map input method to generation method enum
            generation_method_map = {
                "natural_language": GenerationMethod.AI_ASSISTED,
                "markdown_context": GenerationMethod.AI_ASSISTED,
                "file_input": GenerationMethod.AI_ASSISTED,
                "direct_code": GenerationMethod.MANUAL,
                "template": GenerationMethod.TEMPLATE_BASED,
                "test": GenerationMethod.AI_ASSISTED  # For testing
            }
            
            # Map contract type to enum
            contract_type_map = {
                "token": ContractType.TOKEN,
                "nft": ContractType.NFT,
                "defi": ContractType.DEFI,
                "dao": ContractType.GOVERNANCE,
                "marketplace": ContractType.MARKETPLACE,
                "generic": ContractType.CUSTOM,
                "custom": ContractType.CUSTOM
            }
            
            # Map network to enum
            network_map = {
                "mainnet": NetworkType.MAINNET,
                "testnet": NetworkType.TESTNET,
                "emulator": NetworkType.EMULATOR
            }
            
            # Create database record
            contract_record = GeneratedContract(
                name=requirements.get("name", "Contract"),
                contract_type=contract_type_map.get(requirements.get("type", "custom"), ContractType.CUSTOM),
                network=network_map.get(requirements.get("network", "testnet"), NetworkType.TESTNET),
                generation_method=generation_method_map.get(input_method, GenerationMethod.AI_ASSISTED),
                description=requirements.get("description", ""),
                requirements_text=requirements.get("description", ""),
                context_used=json.dumps(requirements.get("context_files", [])) if requirements.get("context_files") else None,
                contract_code=contract_content,
                project_directory=str(Path("/Users/harjjotsinghh/Desktop/Main/D Drive/Projects/smart-contract-llm/flow_projects") / f"{requirements.get('name', 'Contract')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                contract_file_path=str(Path("/Users/harjjotsinghh/Desktop/Main/D Drive/Projects/smart-contract-llm/flow_projects") / f"{requirements.get('name', 'Contract')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}" / "Contract.cdc"),
                generation_time_seconds=int(generation_time),
                has_transactions=bool(result.get("flow_project", {}).get("transactions")),
                has_scripts=bool(result.get("flow_project", {}).get("scripts")),
                has_tests=bool(result.get("flow_project", {}).get("tests")),
                flow_json_config=json.dumps(result.get("flow_project", {}).get("flow_json", {})) if result.get("flow_project", {}).get("flow_json") else None,
                features=json.dumps(requirements.get("features", [])) if requirements.get("features") else None
            )
            
            # Save to database
            db = next(get_db())
            db.add(contract_record)
            db.commit()
            db.refresh(contract_record)
            
            console.print(f"✅ Contract metadata saved to database (ID: {contract_record.id})", style="green")
            
        except Exception as e:
            console.print(f"❌ Failed to save contract to database: {e}", style="red")
            # Don't raise the exception to avoid breaking the main flow