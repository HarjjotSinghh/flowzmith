#!/usr/bin/env python3
"""
Smart Contract LLM Builder CLI Tool

A comprehensive command-line interface for testing and interacting with the Smart Contract LLM Builder application.
Provides step-by-step guided workflows for contract submission, deployment, and management.
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import get_settings
from src.models.database import get_db, create_tables, check_database_connection
from src.cli import APIClient, ContractCreator, DeploymentManager, DocumentationSearch

app = typer.Typer(
    name="smart-contract-cli",
    help="Smart Contract LLM Builder CLI - Test and manage your smart contracts",
    add_completion=False
)

console = Console()


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
    try:
        console.print("🔍 Checking server health...", style="blue")
        async with APIClient() as client:
            response = await client.health_check()
            console.print(f"📡 Server response: {response}", style="dim")
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
        console.print("🔍 Checking database connection...", style="blue")
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

    # Create contract using ContractCreator
    async def create_contract_async():
        async with APIClient() as client:
            creator = ContractCreator(client)
            return await creator.create_contract_interactive()

    result = asyncio.run(create_contract_async())

    if result.get("status") == "success":
        console.print("🎉 Contract creation completed successfully!", style="green")
    elif result.get("status") == "failed":
        console.print(f"❌ Contract creation failed: {result.get('error', 'Unknown error')}", style="red")
        raise typer.Exit(1)


@app.command()
def deploy_contract():
    """Deploy a smart contract to the blockchain."""
    console.print("🚀 Contract Deployment", style="bold blue")

    # Check environment
    async def async_checks():
        server_ok = await check_server_health()
        db_ok = await check_database()
        return server_ok and db_ok

    if not asyncio.run(async_checks()):
        console.print("❌ Cannot proceed without proper setup", style="red")
        raise typer.Exit(1)

    # Deploy contract using DeploymentManager
    async def deploy_contract_async():
        async with APIClient() as client:
            manager = DeploymentManager(client)
            return await manager.deploy_contract_interactive()

    result = asyncio.run(deploy_contract_async())

    if result.get("status") == "success":
        console.print("🎉 Contract deployment completed successfully!", style="green")
    elif result.get("status") == "failed":
        console.print(f"❌ Contract deployment failed: {result.get('error', 'Unknown error')}", style="red")
        raise typer.Exit(1)


@app.command()
def search_docs():
    """Search documentation and knowledge base."""
    console.print("📚 Documentation Search", style="bold blue")

    # Check environment
    async def async_checks():
        server_ok = await check_server_health()
        return server_ok

    if not asyncio.run(async_checks()):
        console.print("❌ Cannot proceed without server connection", style="red")
        raise typer.Exit(1)

    # Search documentation using DocumentationSearch
    async def search_docs_async():
        async with APIClient() as client:
            search = DocumentationSearch(client)
            return await search.search_interactive()

    asyncio.run(search_docs_async())


@app.command()
def upload_docs():
    """Upload documentation to the knowledge base."""
    console.print("📤 Upload Documentation", style="bold blue")

    # Check environment
    async def async_checks():
        server_ok = await check_server_health()
        return server_ok

    if not asyncio.run(async_checks()):
        console.print("❌ Cannot proceed without server connection", style="red")
        raise typer.Exit(1)

    # Upload documentation using DocumentationSearch
    async def upload_docs_async():
        async with APIClient() as client:
            search = DocumentationSearch(client)
            return await search.upload_documentation()

    asyncio.run(upload_docs_async())


@app.command()
def browse_docs():
    """Browse documentation by categories."""
    console.print("📂 Browse Documentation", style="bold blue")

    # Check environment
    async def async_checks():
        server_ok = await check_server_health()
        return server_ok

    if not asyncio.run(async_checks()):
        console.print("❌ Cannot proceed without server connection", style="red")
        raise typer.Exit(1)

    # Browse documentation using DocumentationSearch
    async def browse_docs_async():
        async with APIClient() as client:
            search = DocumentationSearch(client)
            return await search.browse_categories()

    asyncio.run(browse_docs_async())


@app.command()
def list_deployments():
    """List all contract deployments."""
    console.print("📋 Deployment History", style="bold blue")

    # Check environment
    async def async_checks():
        server_ok = await check_server_health()
        return server_ok

    if not asyncio.run(async_checks()):
        console.print("❌ Cannot proceed without server connection", style="red")
        raise typer.Exit(1)

    # List deployments using DeploymentManager
    async def list_deployments_async():
        async with APIClient() as client:
            manager = DeploymentManager(client)
            return await manager.list_deployments()

    asyncio.run(list_deployments_async())


@app.command()
def status():
    """Check system status and statistics."""
    console.print("📊 System Status", style="bold blue")

    # Check server health and get statistics
    async def check_status():
        server_ok = await check_server_health()
        db_ok = await check_database()

        # Get dashboard stats
        try:
            async with APIClient() as client:
                stats = await client.get_dashboard_stats()
                return server_ok, db_ok, stats
        except Exception as e:
            console.print(f"⚠️  Could not fetch statistics: {e}", style="yellow")
            return server_ok, db_ok, {}

    server_ok, db_ok, stats = asyncio.run(check_status())

    # Status table
    from rich.table import Table
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
    console.print("🧙 Smart Contract Creation Wizard", style="bold blue")
    console.print("This wizard will guide you through the entire process of creating and deploying a smart contract.", style="dim")

    # Step 1: Environment check
    console.print("\nStep 1: Environment Check", style="bold blue")
    setup()

    # Step 2: Create contract
    console.print("\nStep 2: Contract Creation", style="bold blue")
    create_contract()

    # Step 3: Deploy contract
    console.print("\nStep 3: Contract Deployment", style="bold blue")
    from rich.prompt import Confirm
    if Confirm.ask("Would you like to deploy a contract now?"):
        deploy_contract()

    console.print("\n🎉 Wizard complete! Your smart contract journey has begun.", style="green")


@app.command()
def version():
    """Show CLI version information."""
    console.print("Smart Contract LLM Builder CLI", style="blue")
    console.print("Version: 1.0.0", style="white")
    console.print("Built with Typer and Rich", style="dim")
    console.print("GitHub: https://github.com/HarjjotSinghh/smart-contract-llm", style="dim")


if __name__ == "__main__":
    app()