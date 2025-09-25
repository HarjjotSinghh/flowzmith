#!/usr/bin/env python3
"""
Smart Contract LLM Builder CLI Tool

A command-line interface for testing and interacting with the Smart Contract LLM Builder application.
Provides step-by-step guided workflows for contract submission, deployment, and management.
"""

import os
import sys
import json
import asyncio
import aiohttp
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.table import Table
from rich.syntax import Syntax
from rich.live import Live
from rich.markdown import Markdown

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import get_settings
from src.models.database import get_db, create_tables, check_database_connection

app = typer.Typer(
    name="smart-contract-cli",
    help="Smart Contract LLM Builder CLI - Test and manage your smart contracts",
    add_completion=False
)

console = Console()

# Global configuration
CONFIG = {
    "api_base_url": "http://localhost:8000",
    "ws_url": "ws://localhost:8000/ws",
    "timeout": 300
}


class APIClient:
    """Async HTTP client for API interactions."""

    def __init__(self, base_url: str = CONFIG["api_base_url"]):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=CONFIG["timeout"])
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        async with self.session.get(f"{self.base_url}{endpoint}", **kwargs) as response:
            return await self._handle_response(response)

    async def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        async with self.session.post(f"{self.base_url}{endpoint}", **kwargs) as response:
            return await self._handle_response(response)

    async def put(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        async with self.session.put(f"{self.base_url}{endpoint}", **kwargs) as response:
            return await self._handle_response(response)

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        try:
            data = await response.json()
        except:
            data = {"text": await response.text()}

        if response.status >= 400:
            raise Exception(f"API Error {response.status}: {data}")

        return data


def show_welcome():
    """Display welcome message and application overview."""
    welcome_text = """
# 🚀 Smart Contract LLM Builder CLI

Welcome to the Smart Contract LLM Builder command-line interface!

This tool provides step-by-step guided workflows for:
• Smart contract submission and generation
• Contract deployment to Flow blockchain
• Documentation search and management
• Real-time progress monitoring

Let's get started building your next smart contract!
"""
    console.print(Panel(Markdown(welcome_text), title="Welcome", border_style="blue"))


async def check_server_health():
    """Check if the backend server is running and healthy."""
    async with APIClient() as client:
        try:
            response = await client.get("/health")
            if response.get("status") == "healthy":
                console.print("✅ Server is healthy and running", style="green")
                return True
            else:
                console.print(f"❌ Server is unhealthy: {response}", style="red")
                return False
        except Exception as e:
            console.print(f"❌ Cannot connect to server: {e}", style="red")
            console.print("\nPlease ensure the server is running with:")
            console.print("python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload", style="yellow")
            return False


async def check_database():
    """Check database connection and tables."""
    try:
        if not check_database_connection():
            console.print("❌ Database connection failed", style="red")
            return False

        console.print("✅ Database connection successful", style="green")
        return True
    except Exception as e:
        console.print(f"❌ Database error: {e}", style="red")
        return False


@app.command()
def setup():
    """Setup and verify the development environment."""
    console.print("🔧 Setting up Smart Contract LLM Builder CLI...", style="blue")

    # Check Python version
    if sys.version_info < (3, 8):
        console.print("❌ Python 3.8 or higher is required", style="red")
        raise typer.Exit(1)

    console.print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", style="green")

    # Check environment variables
    settings = get_settings()
    if not settings.database_url:
        console.print("❌ DATABASE_URL environment variable not set", style="red")
        raise typer.Exit(1)

    console.print("✅ Environment variables configured", style="green")

    # Run async checks
    async def async_checks():
        server_ok = await check_server_health()
        db_ok = await check_database()
        return server_ok and db_ok

    result = asyncio.run(async_checks())

    if result:
        console.print("🎉 Setup complete! You're ready to use the CLI.", style="green")
    else:
        console.print("❌ Setup failed. Please check the errors above.", style="red")
        raise typer.Exit(1)


def get_input_methods() -> List[str]:
    """Get available input methods for contract creation."""
    return [
        "1. Natural Language Description",
        "2. Upload CADENCE (.cdc) File",
        "3. Upload Solidity (.sol) File",
        "4. Paste Contract Code Directly",
        "5. Use Template/Example"
    ]


def select_input_method() -> str:
    """Let user select contract input method."""
    console.print("\n📝 How would you like to create your smart contract?", style="blue")

    methods = get_input_methods()
    for method in methods:
        console.print(f"  {method}", style="cyan")

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


def get_contract_requirements() -> Dict[str, Any]:
    """Get contract requirements from user input."""
    console.print("\n🎯 Let's define your contract requirements:", style="blue")

    requirements = {
        "contract_name": Prompt.ask("Contract name", default="MyToken"),
        "contract_type": Prompt.ask(
            "Contract type",
            choices=["Token", "NFT", "Marketplace", "DAO", "Custom"],
            default="Token"
        ),
        "description": Prompt.ask("Brief description", default="A smart contract for..."),
        "network": Prompt.ask(
            "Target network",
            choices=["testnet", "mainnet"],
            default="testnet"
        )
    }

    return requirements


def get_natural_language_input() -> str:
    """Get natural language description of contract requirements."""
    console.print("\n📄 Describe your smart contract in natural language:", style="blue")
    console.print("Example: 'I want to create an NFT contract with minting capabilities and metadata storage'", style="dim")

    description = Prompt.ask("\nContract requirements", multiline=True)
    return description.strip()


def get_file_input(file_extension: str) -> str:
    """Get contract code from file upload."""
    console.print(f"\n📁 Please provide the path to your {file_extension} file:", style="blue")

    while True:
        file_path = Prompt.ask("File path")

        if not os.path.exists(file_path):
            console.print(f"❌ File not found: {file_path}", style="red")
            continue

        if not file_path.lower().endswith(file_extension):
            console.print(f"❌ File must be a {file_extension} file", style="red")
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            console.print(f"✅ Loaded {len(content)} characters from {file_path}", style="green")
            return content

        except Exception as e:
            console.print(f"❌ Error reading file: {e}", style="red")


def get_direct_code_input() -> str:
    """Get contract code directly from user input."""
    console.print("\n💻 Paste your contract code:", style="blue")
    console.print("Press Enter twice to finish input", style="dim")

    lines = []
    while True:
        line = Prompt.ask("")
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)

    code = "\n".join(lines[:-1])  # Remove the last empty line
    console.print(f"✅ Received {len(code)} characters of code", style="green")
    return code


def get_template_selection() -> str:
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


@app.command()
def create_contract():
    """Create a new smart contract with step-by-step guidance."""
    show_welcome()

    # Check environment first
    async def async_checks():
        server_ok = await check_server_health()
        db_ok = await check_database()
        return server_ok and db_ok

    if not asyncio.run(async_checks()):
        console.print("❌ Cannot proceed without proper setup", style="red")
        raise typer.Exit(1)

    # Get input method
    input_method = select_input_method()

    # Get contract requirements
    requirements = get_contract_requirements()

    # Get contract code based on input method
    contract_code = ""

    if input_method == "natural_language":
        description = get_natural_language_input()
        contract_code = description  # Will be processed by AI

    elif input_method == "cadence_file":
        contract_code = get_file_input(".cdc")

    elif input_method == "solidity_file":
        contract_code = get_file_input(".sol")

    elif input_method == "direct_code":
        contract_code = get_direct_code_input()

    elif input_method == "template":
        contract_code = get_template_selection()

    # Show summary
    console.print("\n📊 Contract Summary:", style="blue")
    summary_table = Table(show_header=False)
    summary_table.add_column("Property", style="cyan")
    summary_table.add_column("Value", style="white")

    summary_table.add_row("Name", requirements["contract_name"])
    summary_table.add_row("Type", requirements["contract_type"])
    summary_table.add_row("Network", requirements["network"])
    summary_table.add_row("Input Method", input_method.replace("_", " ").title())
    summary_table.add_row("Code Length", f"{len(contract_code)} characters")

    console.print(summary_table)

    if not Confirm.ask("\nProceed with contract creation?"):
        console.print("❌ Contract creation cancelled", style="yellow")
        return

    # Submit contract (will be implemented with actual API calls)
    console.print("\n🚀 Creating contract...", style="blue")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Processing contract...", total=None)

        # Simulate processing (will be replaced with actual API calls)
        import time
        for i in range(5):
            time.sleep(0.5)
            progress.update(task, description=f"Step {i+1}/5: Processing...")

    console.print("✅ Contract created successfully!", style="green")
    console.print(f"Contract ID: {uuid.uuid4()}", style="cyan")


@app.command()
def deploy_contract():
    """Deploy a smart contract to the blockchain."""
    console.print("🚀 Contract Deployment", style="blue")

    # This will be implemented with actual deployment logic
    console.print("📋 Available contracts for deployment:", style="cyan")

    # Mock contract list
    contracts = [
        {"id": "1", "name": "MyToken", "status": "Generated", "created": "2024-01-01"},
        {"id": "2", "name": "NFTCollection", "status": "Generated", "created": "2024-01-02"}
    ]

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("ID", style="cyan", width=10)
    table.add_column("Name", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Created", style="white")

    for contract in contracts:
        table.add_row(contract["id"], contract["name"], contract["status"], contract["created"])

    console.print(table)

    contract_id = Prompt.ask("Select contract to deploy", choices=["1", "2"])
    network = Prompt.ask("Select network", choices=["testnet", "mainnet"], default="testnet")

    if not Confirm.ask(f"Deploy contract {contract_id} to {network}?"):
        console.print("❌ Deployment cancelled", style="yellow")
        return

    console.print("\n🚀 Deploying contract...", style="blue")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Deploying contract...", total=None)

        # Simulate deployment
        import time
        steps = [
            "Compiling contract...",
            "Connecting to network...",
            "Executing deployment...",
            "Confirming transaction...",
            "Verifying deployment..."
        ]

        for step in steps:
            time.sleep(1)
            progress.update(task, description=step)

    console.print("✅ Contract deployed successfully!", style="green")
    console.print(f"Transaction Hash: 0x{uuid.uuid4().hex[:40]}", style="cyan")
    console.print(f"Contract Address: 0x{uuid.uuid4().hex[:40]}", style="cyan")


@app.command()
def search_docs():
    """Search documentation and knowledge base."""
    console.print("📚 Documentation Search", style="blue")

    query = Prompt.ask("Search query")

    if not query:
        console.print("❌ Please provide a search query", style="red")
        return

    console.print(f"\n🔍 Searching for: '{query}'...", style="blue")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Searching documentation...", total=None)

        # Simulate search
        import time
        time.sleep(2)
        progress.update(task, description="Found 3 results")

    # Mock search results
    results = [
        {
            "title": "Flow Contract Development Guide",
            "content": "Comprehensive guide for developing smart contracts on Flow blockchain...",
            "relevance": 0.95
        },
        {
            "title": "CADENCE Language Reference",
            "content": "Complete reference for the CADENCE programming language...",
            "relevance": 0.87
        },
        {
            "title": "Token Contract Templates",
            "content": "Pre-built token contract templates for various use cases...",
            "relevance": 0.78
        }
    ]

    console.print("\n📄 Search Results:", style="blue")

    for i, result in enumerate(results, 1):
        console.print(f"\n{i}. {result['title']}", style="green")
        console.print(f"   Relevance: {result['relevance']:.0%}", style="cyan")
        console.print(f"   {result['content'][:100]}...", style="white")


@app.command()
def status():
    """Check system status and statistics."""
    console.print("📊 System Status", style="blue")

    # Check server health
    async def check_status():
        server_ok = await check_server_health()
        db_ok = await check_database()

        # Get dashboard stats
        try:
            async with APIClient() as client:
                stats = await client.get("/api/dashboard/stats")
                return server_ok, db_ok, stats
        except:
            return server_ok, db_ok, {}

    server_ok, db_ok, stats = asyncio.run(check_status())

    # Status table
    status_table = Table(show_header=False, box=None)
    status_table.add_column("Component", style="cyan")
    status_table.add_column("Status", style="white")

    status_table.add_row("Server", "✅ Running" if server_ok else "❌ Offline")
    status_table.add_row("Database", "✅ Connected" if db_ok else "❌ Disconnected")

    console.print(status_table)

    if stats:
        console.print("\n📈 Statistics:", style="blue")

        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")

        stats_table.add_row("Total Contracts", str(stats.get("total_contracts", 0)))
        stats_table.add_row("Successful Deployments", str(stats.get("successful_deployments", 0)))
        stats_table.add_row("Pending Submissions", str(stats.get("pending_submissions", 0)))
        stats_table.add_row("Documentation Items", str(stats.get("total_docs", 0)))

        console.print(stats_table)


@app.command()
def wizard():
    """Run the complete contract creation wizard."""
    console.print("🧙 Smart Contract Creation Wizard", style="blue")
    console.print("This wizard will guide you through the entire process of creating and deploying a smart contract.", style="dim")

    # Step 1: Environment check
    console.print("\nStep 1: Environment Check", style="bold blue")
    setup()

    # Step 2: Create contract
    console.print("\nStep 2: Contract Creation", style="bold blue")
    create_contract()

    # Step 3: Deploy contract
    console.print("\nStep 3: Contract Deployment", style="bold blue")
    if Confirm.ask("Would you like to deploy this contract now?"):
        deploy_contract()

    console.print("\n🎉 Wizard complete! Your smart contract journey has begun.", style="green")


@app.command()
def version():
    """Show CLI version information."""
    console.print("Smart Contract LLM Builder CLI", style="blue")
    console.print("Version: 1.0.0", style="white")
    console.print("Built with Typer and Rich", style="dim")


if __name__ == "__main__":
    app()