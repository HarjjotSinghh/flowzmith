"""
Contract creation functionality for the CLI.

Handles step-by-step contract creation with various input methods.
"""

import os
import uuid
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

console = Console()

class ContractCreator:
    """Handles smart contract creation process."""

    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    async def create_contract_interactive(self) -> Dict[str, Any]:
        """Guide user through interactive contract creation."""
        console.print("🚀 Smart Contract Creation", style="bold blue")
        console.print("Let's create your smart contract step by step.", style="dim")

        # Step 1: Select input method
        input_method = await self._select_input_method()

        # Step 2: Get contract requirements
        requirements = await self._get_contract_requirements()

        # Step 3: Get contract content
        contract_content = await self._get_contract_content(input_method)

        # Step 4: Review and confirm
        if await self._review_contract(requirements, contract_content):
            return await self._submit_contract(requirements, contract_content, input_method)
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
            ("5", "Use Template/Example", "Start from pre-built template")
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
            choices=["1", "2", "3", "4", "5"],
            default="1"
        )

        method_map = {
            "1": "natural_language",
            "2": "cadence_file",
            "3": "solidity_file",
            "4": "direct_code",
            "5": "template"
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

        # Connect to WebSocket for real-time updates
        try:
            connection_id = await self.api_client.connect_websocket()
            console.print(f"✅ Connected to real-time updates (ID: {connection_id})", style="green")
        except Exception as e:
            console.print(f"⚠️  WebSocket connection failed: {e}", style="yellow")
            console.print("Continuing without real-time updates...", style="dim")

        # Submit contract with progress tracking
        result = await self._submit_with_progress(contract_data)

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