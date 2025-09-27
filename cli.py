#!/usr/bin/env python3
"""
Flowzmith CLI Tool

A comprehensive command-line interface for testing and interacting with the Flowzmith application.
Provides step-by-step guided workflows for contract submission, deployment, and management.
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# Load .env file
load_dotenv()

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import get_settings
from src.models.database import get_db, create_tables, check_database_connection
from src.cli import APIClient, ContractCreator, DeploymentManager, DocumentationSearch
from src.cli.flow_manager import FlowProjectManager
from src.cli.deployment_service import ContractDeploymentService
from rich.text import Text

banner = """
 ███████╗ ██╗       ██████╗  ██╗    ██╗ ███████╗ ███╗   ███╗ ██╗ ████████╗ ██╗  ██╗
 ██╔════╝ ██║      ██╔═══██╗ ██║    ██║ ╚══███╔╝ ████╗ ████║ ██║ ╚══██╔══╝ ██║  ██║
 █████╗   ██║      ██║   ██║ ██║ █╗ ██║   ███╔╝  ██╔████╔██║ ██║    ██║    ███████║
 ██╔══╝   ██║      ██║   ██║ ██║███╗██║  ███╔╝   ██║╚██╔╝██║ ██║    ██║    ██╔══██║
 ██║      ███████╗ ╚██████╔╝ ╚███╔███╔╝ ███████╗ ██║ ╚═╝ ██║ ██║    ██║    ██║  ██║
 ╚═╝      ╚══════╝  ╚═════╝   ╚══╝╚══╝  ╚══════╝ ╚═╝     ╚═╝ ╚═╝    ╚═╝    ╚═╝  ╚═╝
"""


async def handle_flow_automation(
    client, contract_content, config_content, contract_name, network, auto_deploy, flow_init
):
    """Handle Flow CLI automation for contract deployment."""
    try:
        flow_manager = FlowProjectManager()
        deployment_service = ContractDeploymentService(client)
        
        if flow_init:
            console.print("\n🔧 Initializing Flow project...", style="blue")
            project_path = await flow_manager.init_project(contract_name)
            console.print(f"✅ Flow project initialized at: {project_path}", style="green")
            
            # Write contract and config files
            await flow_manager.write_contract_files(
                project_path, contract_name, contract_content, config_content
            )
            console.print("✅ Contract files written", style="green")
            
        if auto_deploy:
            console.print("\n🚀 Starting automatic deployment...", style="blue")
            deployment_result = await deployment_service.deploy_with_flow_cli(
                contract_content, config_content, contract_name, network
            )
            
            if deployment_result.get("success"):
                console.print("✅ Contract deployed successfully!", style="green")
                console.print(f"Transaction ID: {deployment_result.get('transaction_id')}", style="cyan")
            else:
                console.print(f"❌ Deployment failed: {deployment_result.get('error')}", style="red")
                
    except Exception as e:
        console.print(f"❌ Flow automation failed: {e}", style="red")
        logger.exception("Flow automation error")

app = typer.Typer(
    name="smart-contract-cli",
    help="Flowzmith CLI - Test and manage your smart contracts",
    add_completion=False
)

console = Console()


def show_welcome():
    """Display welcome message and application overview."""
    # Build gradient banner: teal → cyan → light cyan
    gradient_lines = []
    # Use direct RGB values instead of Color object attributes
    base_r, base_g, base_b = 0, 128, 128  # teal
    target_r, target_g, target_b = 160, 216, 232  # light cyan
    
    banner_lines = banner.strip("\n").splitlines()
    for i, line in enumerate(banner_lines):
        factor = i / max(1, len(banner_lines) - 1)  # 0 → 1 across all lines
        r = int(base_r + (target_r - base_r) * factor)
        g = int(base_g + (target_g - base_g) * factor)
        b = int(base_b + (target_b - base_b) * factor)
        gradient_lines.append(f"[rgb({r},{g},{b})]{line}[/]")
    console.print("\n")
    console.print("\n".join(gradient_lines))
    console.print("\n")

    welcome_text = f"""
# 🚀 Flowzmith CLI

Welcome to the Flowzmith command-line interface!

This tool provides step-by-step guided workflows for:\n
• Smart contract submission and generation\n
• Contract deployment to Flow blockchain\n
• Documentation search and management\n
• Real-time progress monitoring

Let's get started building your next smart contract!
"""
    console.print(Panel(Markdown(welcome_text), title="Welcome", border_style="blue"))


import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)
    

async def check_server_health():
    """Check if the backend server is running and healthy."""
    try:
        logger.info("Starting server health check")
        console.print("🔍 Checking server health...", style="blue")
        async with APIClient() as client:
            response = await client.health_check()
            logger.info("/health response: %s", response)
            console.print(f"📡 Server response: {response}", style="dim")
            if response.get("status") == "healthy":
                console.print("✅ Server is healthy and running", style="green")
                return True
            else:
                console.print(f"❌ Server is unhealthy: {response}", style="red")
                return False
    except Exception as e:
        logger.exception("Server health check failed")
        console.print(f"❌ Cannot connect to server: {e}", style="red")
        console.print("\nPlease ensure the server is running with:")
        console.print("python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload", style="yellow")
        return False


async def check_database():
    """Check database connection and tables."""
    try:
        logger.info("Starting database check")
        console.print("🔍 Checking database connection...", style="blue")
        if not check_database_connection():
            logger.error("Database connection failed")
            console.print("❌ Database connection failed", style="red")
            return False

        logger.info("Database connection successful")
        console.print("✅ Database connection successful", style="green")
        return True
    except Exception as e:
        logger.exception("Database check raised exception")
        console.print(f"❌ Database error: {e}", style="red")
        return False


@app.command()
def setup():
    """Setup and verify the development environment."""
    logger.info("Running setup command")
    console.print("🔧 Setting up Flowzmith CLI...", style="blue")
    # load env vars and check status
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    groq_api_key = os.getenv("GROQ_API_KEY")
 
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python version check failed: %s", sys.version_info)
        console.print("❌ Python 3.8 or higher is required", style="red")
        raise typer.Exit(1)

    console.print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", style="green")

    # Check environment variables
    settings = get_settings()
    if not settings.database_url:
        logger.error("DATABASE_URL not set in environment")
        console.print("❌ DATABASE_URL environment variable not set", style="red")
        raise typer.Exit(1)

    logger.info("Environment variables OK")
    console.print("✅ Environment variables configured", style="green")

    # Run async checks
    async def async_checks():
        logger.info("Running async checks for setup")
        server_ok = await check_server_health()
        db_ok = await check_database()
        logger.info("Async checks finished: server_ok=%s db_ok=%s", server_ok, db_ok)
        return server_ok and db_ok

    result = asyncio.run(async_checks())

    if result:
        logger.info("Setup completed successfully")
        console.print("🎉 Setup complete! You're ready to use the CLI.", style="green")
    else:
        logger.error("Setup failed")
        console.print("❌ Setup failed. Please check the errors above.", style="red")
        raise typer.Exit(1)


@app.command()
def flow_auto():
    """Automated Flow workflow: Generate contract, create MCP server, and deploy to Flow."""
    logger.info("Running flow_auto command")
    show_welcome()
    console.print("🚀 Automated Flow Workflow", style="bold blue")
    console.print("This will generate a contract, create an MCP server, and deploy to Flow blockchain.", style="cyan")

    # Check environment
    async def async_checks():
        logger.info("Running async checks for flow_auto")
        server_ok = await check_server_health()
        db_ok = await check_database()
        logger.info("Async checks finished: server_ok=%s db_ok=%s", server_ok, db_ok)
        return server_ok and db_ok

    if not asyncio.run(async_checks()):
        logger.error("Environment checks failed for flow_auto")
        console.print("❌ Cannot proceed without server and database connection", style="red")
        raise typer.Exit(1)

    # Run interactive automated workflow
    async def run_automated_workflow():
        async with APIClient() as client:
            creator = ContractCreator(client)
            logger.info("Starting interactive automated Flow workflow")
            result = await creator.create_contract_interactive()
            logger.info("Automated Flow workflow result: %s", result)
            return result

    result = asyncio.run(run_automated_workflow())

    if result.get("status") == "success":
        console.print("🎉 Automated Flow workflow completed successfully!", style="green")
    elif result.get("status") == "failed":
        logger.error("Automated Flow workflow failed: %s", result)
        console.print(f"❌ Automated Flow workflow failed: {result.get('error', 'Unknown error')}", style="red")
        raise typer.Exit(1)


@app.command()
def create_contract():
    """Create a new smart contract with step-by-step guidance."""
    logger.info("Running create_contract command")
    show_welcome()

    # Check environment first
    async def async_checks():
        logger.info("Running async checks for create_contract")
        server_ok = await check_server_health()
        db_ok = await check_database()
        logger.info("Async checks finished: server_ok=%s db_ok=%s", server_ok, db_ok)
        return server_ok and db_ok

    if not asyncio.run(async_checks()):
        logger.error("Environment checks failed for create_contract")
        console.print("❌ Cannot proceed without proper setup", style="red")
        raise typer.Exit(1)

    # Create contract using ContractCreator
    async def create_contract_async():
        async with APIClient() as client:
            creator = ContractCreator(client)
            logger.info("Starting interactive contract creation")
            result = await creator.create_contract_interactive()
            logger.info("Contract creation result: %s", result)
            return result

    result = asyncio.run(create_contract_async())

    if result.get("status") == "success":
        console.print("🎉 Contract creation completed successfully!", style="green")
    elif result.get("status") == "failed":
        logger.error("Contract creation failed: %s", result)
        console.print(f"❌ Contract creation failed: {result.get('error', 'Unknown error')}", style="red")
        raise typer.Exit(1)


@app.command()
def deploy_contract():
    """Deploy a smart contract to the blockchain."""
    logger.info("Running deploy_contract command")
    console.print("🚀 Contract Deployment", style="bold blue")

    # Check environment
    async def async_checks():
        logger.info("Running async checks for deploy_contract")
        server_ok = await check_server_health()
        db_ok = await check_database()
        logger.info("Async checks finished: server_ok=%s db_ok=%s", server_ok, db_ok)
        return server_ok and db_ok

    if not asyncio.run(async_checks()):
        logger.error("Environment checks failed for deploy_contract")
        console.print("❌ Cannot proceed without proper setup", style="red")
        raise typer.Exit(1)

    # Deploy contract using DeploymentManager
    async def deploy_contract_async():
        async with APIClient() as client:
            manager = DeploymentManager(client)
            logger.info("Starting interactive deployment")
            result = await manager.deploy_contract_interactive()
            logger.info("Deployment result: %s", result)
            return result

    result = asyncio.run(deploy_contract_async())

    if result.get("status") == "success":
        console.print("🎉 Contract deployment completed successfully!", style="green")
    elif result.get("status") == "failed":
        logger.error("Deployment failed: %s", result)
        console.print(f"❌ Contract deployment failed: {result.get('error', 'Unknown error')}", style="red")
        raise typer.Exit(1)


@app.command()
def search_docs():
    """Search documentation and knowledge base."""
    logger.info("Running search_docs command")
    console.print("📚 Documentation Search", style="bold blue")

    # Check environment
    async def async_checks():
        logger.info("Running async checks for search_docs")
        server_ok = await check_server_health()
        logger.info("Async checks finished: server_ok=%s", server_ok)
        return server_ok

    if not asyncio.run(async_checks()):
        logger.error("Environment checks failed for search_docs")
        console.print("❌ Cannot proceed without server connection", style="red")
        raise typer.Exit(1)

    # Search documentation using DocumentationSearch
    async def search_docs_async():
        async with APIClient() as client:
            search = DocumentationSearch(client)
            logger.info("Starting documentation search interactive flow")
            return await search.search_interactive()

    asyncio.run(search_docs_async())


@app.command()
def upload_docs():
    """Upload documentation to the knowledge base."""
    logger.info("Running upload_docs command")
    console.print("📤 Upload Documentation", style="bold blue")

    # Check environment
    async def async_checks():
        logger.info("Running async checks for upload_docs")
        server_ok = await check_server_health()
        logger.info("Async checks finished: server_ok=%s", server_ok)
        return server_ok

    if not asyncio.run(async_checks()):
        logger.error("Environment checks failed for upload_docs")
        console.print("❌ Cannot proceed without server connection", style="red")
        raise typer.Exit(1)

    # Upload documentation using DocumentationSearch
    async def upload_docs_async():
        async with APIClient() as client:
            search = DocumentationSearch(client)
            logger.info("Starting documentation upload interactive flow")
            return await search.upload_documentation()

    asyncio.run(upload_docs_async())


@app.command()
def browse_docs():
    """Browse documentation by categories."""
    logger.info("Running browse_docs command")
    console.print("📂 Browse Documentation", style="bold blue")

    # Check environment
    async def async_checks():
        logger.info("Running async checks for browse_docs")
        server_ok = await check_server_health()
        logger.info("Async checks finished: server_ok=%s", server_ok)
        return server_ok

    if not asyncio.run(async_checks()):
        logger.error("Environment checks failed for browse_docs")
        console.print("❌ Cannot proceed without server connection", style="red")
        raise typer.Exit(1)

    # Browse documentation using DocumentationSearch
    async def browse_docs_async():
        async with APIClient() as client:
            search = DocumentationSearch(client)
            logger.info("Starting documentation browse interactive flow")
            return await search.browse_categories()

    asyncio.run(browse_docs_async())


@app.command()
def list_deployments():
    """List all contract deployments."""
    logger.info("Running list_deployments command")
    console.print("📋 Deployment History", style="bold blue")

    # Check environment
    async def async_checks():
        logger.info("Running async checks for list_deployments")
        server_ok = await check_server_health()
        logger.info("Async checks finished: server_ok=%s", server_ok)
        return server_ok

    if not asyncio.run(async_checks()):
        logger.error("Environment checks failed for list_deployments")
        console.print("❌ Cannot proceed without server connection", style="red")
        raise typer.Exit(1)

    # List deployments using DeploymentManager
    async def list_deployments_async():
        async with APIClient() as client:
            manager = DeploymentManager(client)
            logger.info("Starting deployments list flow")
            return await manager.list_deployments()

    asyncio.run(list_deployments_async())


@app.command()
def status():
    """Check system status and statistics."""
    logger.info("Running status command")
    console.print("📊 System Status", style="bold blue")

    # Check server health and get statistics
    async def check_status():
        logger.info("Running async checks for status")
        server_ok = await check_server_health()
        db_ok = await check_database()
        logger.info("Async checks finished: server_ok=%s db_ok=%s", server_ok, db_ok)

        # Get dashboard stats
        try:
            async with APIClient() as client:
                stats = await client.get_dashboard_stats()
                logger.info("Dashboard stats fetched: %s", stats)
                return server_ok, db_ok, stats
        except Exception as e:
            logger.exception("Could not fetch dashboard stats")
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
    logger.info("Running wizard command")
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

    logger.info("Wizard complete")
    console.print("\n🎉 Wizard complete! Your smart contract journey has begun.", style="green")


@app.command()
def version():
    """Show CLI version information."""
    logger.info("Running version command")
    console.print("Flowzmith CLI", style="blue")
    console.print("Version: 1.0.0", style="white")
    console.print("Built with Typer and Rich", style="dim")
    console.print("GitHub: https://github.com/HarjjotSinghh/smart-contract-llm", style="dim")


@app.command("generate-from-context")
def generate_from_context(
    requirements: str = typer.Option(None, help="High-level contract requirements in natural language"),
    context_dir: Path = typer.Option(Path("context"), help="Directory containing .md files to use as context"),
    network: str = typer.Option("emulator", help="Target network for configuration (emulator|testnet|mainnet)"),
    stream: bool = typer.Option(True, help="Use streaming mode for real-time progress updates"),
    auto_deploy: bool = typer.Option(False, help="Automatically create Flow project and deploy contract"),
    flow_init: bool = typer.Option(False, help="Initialize Flow project with flow init command")
):
    """Generate a Cadence contract using local markdown context and print results."""

    async def _run():
        # Read all markdown files
        context_pieces = []
        if context_dir.exists() and context_dir.is_dir():
            for p in sorted(context_dir.rglob("*.md")):
                try:
                    text = p.read_text(encoding="utf-8", errors="ignore")
                    header = f"\n### {p.name}\n\n"
                    context_pieces.append(header + text)
                except Exception:
                    pass
        context_text = "\n\n".join(context_pieces)

        # Prompt for requirements if not provided
        reqs = requirements or typer.prompt("Describe the contract you want to build")

        payload = {
            "requirements": reqs,
            "context": context_text,
            "pre_conditions": {},
            "post_conditions": {},
            "network": network,
        }

        if auto_deploy or flow_init:
            console.print(f"🔧 Flow CLI automation enabled: {'Auto-deploy' if auto_deploy else 'Flow init only'}", style="yellow")

        # Call API and print results
        from src.cli.api_client import APIClient
        async with APIClient() as client:
            try:
                if stream:
                    # Use streaming mode with live output
                    console.print("🔄 Starting contract generation with streaming...", style="blue")
                    
                    streamed_text = ""
                    config_content = None
                    contract_content = None
                    contract_name = None
                    
                    async for chunk in client.stream_generate_contract_with_context(payload):
                        if chunk.get("type") == "content":
                            content = chunk.get("chunk", "")
                            streamed_text += content
                            # Print streamed content in real-time
                            sys.stdout.write(content)
                            sys.stdout.flush()
                            # Try to extract config if markers present
                            if config_content is None and "<!-- CONFIG_START -->" in streamed_text and "<!-- CONFIG_END -->" in streamed_text:
                                start = streamed_text.find("<!-- CONFIG_START -->") + len("<!-- CONFIG_START -->")
                                end = streamed_text.find("<!-- CONFIG_END -->")
                                if start > 0 and end > start:
                                    config_content = streamed_text[start:end].strip()
                            # Capture contract content
                            if contract_content is None:
                                contract_content = content
                            else:
                                contract_content += content
                        elif chunk.get("type") == "error":
                            error_msg = chunk.get("error", "Unknown error")
                            typer.secho(f"\n❌ Generation failed: {error_msg}", fg=typer.colors.RED)
                            return
                        elif chunk.get("type") == "status":
                            status_data = chunk.get("data", {})
                            stage = status_data.get("stage")
                            if stage:
                                console.print(f"\n✅ {stage}", style="green")
                        elif chunk.get("type") == "progress":
                            progress_data = chunk.get("data", {})
                            msg = progress_data.get("message")
                            if msg:
                                console.print(f"⚡ {msg}", style="cyan")
                        elif chunk.get("type") == "contract_name":
                            contract_name = chunk.get("name")
                        elif chunk.get("type") == "complete":
                            # Completed - break loop
                            pass
                    
                    # Print final results
                    typer.secho("\n\n=== Generated flow.json ===\n", fg=typer.colors.GREEN)
                    try:
                        if config_content:
                            # If config is JSON, pretty print; otherwise print raw
                            try:
                                typer.echo(json.dumps(json.loads(config_content), indent=2))
                            except Exception:
                                typer.echo(config_content)
                        else:
                            typer.echo("No configuration data detected in stream.")
                    except Exception:
                        typer.echo(str(config_content))
                    
                    typer.secho("\n✅ Contract generation completed successfully!", fg=typer.colors.GREEN)
                    
                    # Handle Flow CLI automation
                    if (flow_init or auto_deploy) and contract_content and config_content:
                        await handle_flow_automation(
                            client, contract_content, config_content, 
                            contract_name or "Contract", network, auto_deploy, flow_init
                        )
                    
                else:
                    # Use non-streaming mode
                    result = await client.generate_contract_with_context(payload)
                    
                    # Pretty print outputs
                    typer.secho("\n=== Generated Cadence Contract (.cdc) ===\n", fg=typer.colors.GREEN)
                    typer.echo(result.get("generated_contract_code", ""))

                    typer.secho("\n=== Generated flow.json ===\n", fg=typer.colors.GREEN)
                    try:
                        cfg = result.get("config_content", {})
                        typer.echo(json.dumps(cfg, indent=2))
                    except Exception:
                        typer.echo(str(result.get("config_content")))

                    typer.secho("\nSaved to project ID:", fg=typer.colors.CYAN)
                    typer.echo(str(result.get("submission_id")))
                    
                    # Handle Flow CLI automation
                    if (flow_init or auto_deploy) and result.get("generated_contract_code") and result.get("config_content"):
                        await handle_flow_automation(
                            client, result.get("generated_contract_code"), result.get("config_content"),
                            result.get("contract_name", "Contract"), network, auto_deploy, flow_init
                        )
                    
            except Exception as e:
                typer.secho(f"Generation failed: {e}", fg=typer.colors.RED)
                return

    asyncio.run(_run())


@app.command()
def mcp_explorer():
    """Use MCP server to explore Flow blockchain."""
    logger.info("Running mcp_explorer command")
    console.print("🔍 Flow Blockchain Explorer (MCP)", style="bold blue")
    console.print("This command uses the MCP server to interact with Flow blockchain.", style="dim")

    # Import and use MCP client
    try:
        from flow_mcp.mcp_client import MCPFlowClient

        async def explore_flow():
            console.print("Connecting to MCP server...", style="blue")
            client = MCPFlowClient()
            await client.connect()

            try:
                # List accounts
                console.print("\n📋 Available Accounts:", style="cyan")
                accounts = await client.list_accounts()
                typer.echo(json.dumps(accounts, indent=2))

                # Interactive menu
                while True:
                    console.print("\n🔧 Available Actions:", style="cyan")
                    console.print("1. View Account Details")
                    console.print("2. View Contract")
                    console.print("3. View Transaction")
                    console.print("4. List Recent Transactions")
                    console.print("5. Exit")

                    choice = typer.prompt("Select action (1-5)", type=int)

                    if choice == 1:
                        address = typer.prompt("Enter account address")
                        result = await client.view_account(address)
                        typer.echo(json.dumps(result, indent=2))
                    elif choice == 2:
                        address = typer.prompt("Enter contract address")
                        name = typer.prompt("Enter contract name")
                        result = await client.view_contract(address, name)
                        typer.echo(json.dumps(result, indent=2))
                    elif choice == 3:
                        tx_id = typer.prompt("Enter transaction ID")
                        result = await client.view_transaction(tx_id)
                        typer.echo(json.dumps(result, indent=2))
                    elif choice == 4:
                        address = typer.prompt("Enter address (optional, press Enter to skip)", default="")
                        result = await client.list_transactions(address if address else None)
                        typer.echo(json.dumps(result, indent=2))
                    elif choice == 5:
                        break
                    else:
                        console.print("Invalid choice. Please try again.", style="red")

            finally:
                await client.disconnect()

        asyncio.run(explore_flow())

    except ImportError as e:
        console.print(f"❌ MCP client not available: {e}", style="red")
        console.print("Please install MCP dependencies: pip install -r flow_mcp/requirements.txt", style="yellow")
        raise typer.Exit(1)


@app.command("flow-init")
def flow_init_project(
    name: str = typer.Option(None, help="Project name (auto-generated if not provided)"),
    directory: Path = typer.Option(None, help="Custom directory for the project")
):
    """Initialize a new Flow project with flow init command."""
    async def run():
        try:
            from datetime import datetime
            flow_manager = FlowProjectManager()
            
            project_name = name if name else f"FlowProject_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            console.print(f"[bold blue]Initializing Flow project:[/bold blue] {project_name}")
            
            # Create a basic Flow project
            result = await flow_manager.create_flow_project(
                project_id=project_name,
                contract_name="HelloWorld",
                contract_content="""
// HelloWorld.cdc
// A simple Hello World contract for Flow blockchain

access(all) contract HelloWorld {
    access(all) var greeting: String

    init() {
        self.greeting = "Hello, World!"
    }

    access(all) fun hello(): String {
        return self.greeting
    }

    access(all) fun changeGreeting(newGreeting: String) {
        self.greeting = newGreeting
    }
}
""".strip(),
                network="emulator"
            )
            
            if result.get("status") == "success":
                console.print(f"[bold green]✅ Flow project initialized successfully![/bold green]")
                console.print(f"[bold cyan]Project path:[/bold cyan] {result.get('project_dir')}")
                
                # Show project status
                status = await flow_manager.get_project_status(project_name)
                console.print(f"[bold cyan]Project status:[/bold cyan]")
                for key, value in status.items():
                    console.print(f"  {key}: {value}")
            else:
                console.print(f"[bold red]❌ Failed to initialize project:[/bold red] {result.get('error')}")
                
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
    
    asyncio.run(run())


@app.command("flow-deploy")
def flow_deploy_contract(
    project_path: Path = typer.Argument(..., help="Path to Flow project directory"),
    network: str = typer.Option("emulator", help="Target network (emulator|testnet|mainnet)"),
    contract_name: str = typer.Option(None, help="Specific contract to deploy")
):
    """Deploy contracts in a Flow project using flow project deploy."""
    async def run():
        try:
            flow_manager = FlowProjectManager()
            
            console.print(f"[bold blue]Deploying contracts from:[/bold blue] {project_path}")
            console.print(f"[bold blue]Target network:[/bold blue] {network}")
            
            # Extract project name from path
            project_name = Path(project_path).name
            result = await flow_manager.deploy_contract(project_name, network)
            
            if result.get("success"):
                console.print(f"[bold green]✅ Deployment successful![/bold green]")
                if result.get("transaction_id"):
                    console.print(f"[bold cyan]Transaction ID:[/bold cyan] {result['transaction_id']}")
                if result.get("output"):
                    console.print(f"[bold cyan]Output:[/bold cyan]")
                    console.print(result["output"])
            else:
                console.print(f"[bold red]❌ Deployment failed:[/bold red] {result.get('error')}")
                
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
    
    asyncio.run(run())


@app.command("flow-status")
def flow_project_status(
    project_path: Path = typer.Argument(..., help="Path to Flow project directory")
):
    """Get status information for a Flow project."""
    async def run():
        try:
            flow_manager = FlowProjectManager()
            
            console.print(f"[bold blue]Getting status for:[/bold blue] {project_path}")
            
            status = await flow_manager.get_project_status(str(project_path))
            
            console.print(f"[bold green]Project Status:[/bold green]")
            for key, value in status.items():
                console.print(f"  [bold cyan]{key}:[/bold cyan] {value}")
                
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
    
    asyncio.run(run())


@app.command("flow-list")
def flow_list_projects():
    """List all Flow projects in the flow_projects directory."""
    async def run():
        try:
            flow_manager = FlowProjectManager()
            
            projects = await flow_manager.list_projects()
            
            if projects:
                console.print(f"[bold green]Found {len(projects)} Flow projects:[/bold green]")
                for project in projects:
                    console.print(f"  [bold cyan]•[/bold cyan] {project['name']} ({project['path']})")
                    if project.get('contracts'):
                        console.print(f"    Contracts: {', '.join(project['contracts'])}")
            else:
                console.print("[bold yellow]No Flow projects found.[/bold yellow]")
                
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
    
    asyncio.run(run())


@app.command("flow-generate-deploy")
def flow_generate_and_deploy(
    requirements: str = typer.Option(None, help="Contract requirements"),
    context_dir: Path = typer.Option(Path("context"), help="Context directory"),
    network: str = typer.Option("emulator", help="Target network"),
    project_name: str = typer.Option(None, help="Custom project name")
):
    """Generate a contract and automatically deploy it using Flow CLI."""
    async def run():
        try:
            from datetime import datetime
            client = APIClient()
            deployment_service = ContractDeploymentService(client)
            
            # Use local variables to avoid scope issues
            req_text = requirements
            proj_name = project_name
            
            if not req_text:
                req_text = typer.prompt("Enter contract requirements")
            
            if not proj_name:
                proj_name = f"Contract_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            console.print(f"[bold blue]Generating and deploying contract:[/bold blue] {proj_name}")
            console.print(f"[bold blue]Requirements:[/bold blue] {req_text}")
            
            # Generate contract
            generation_request = {
                "requirements": req_text,
                "context_dir": str(context_dir),
                "network": network
            }
            result = await client.generate_contract_with_context(generation_request)
            
            if not result.get("success"):
                console.print(f"[bold red]Contract generation failed:[/bold red] {result.get('error')}")
                return
            
            console.print("[bold green]✅ Contract generated successfully![/bold green]")
            
            # Deploy with Flow CLI
            deployment_result = await deployment_service.deploy_with_flow_cli(
                result.get("contract"), 
                result.get("flow_json"), 
                proj_name, 
                network
            )
            
            if deployment_result.get("success"):
                console.print("[bold green]✅ Contract deployed successfully![/bold green]")
                console.print(f"[bold cyan]Project path:[/bold cyan] {deployment_result.get('project_path')}")
                if deployment_result.get("transaction_id"):
                    console.print(f"[bold cyan]Transaction ID:[/bold cyan] {deployment_result['transaction_id']}")
            else:
                console.print(f"[bold red]❌ Deployment failed:[/bold red] {deployment_result.get('error')}")
                
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
    
    asyncio.run(run())


if __name__ == "__main__":
    app()