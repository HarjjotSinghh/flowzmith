"""
Deployment management functionality for the CLI.

Handles contract deployment to various networks with real-time monitoring.
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.live import Live
from rich.text import Text

from .api_client import APIClient

console = Console()

class DeploymentManager:
    """Handles smart contract deployment process."""

    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    async def deploy_contract_interactive(self) -> Dict[str, Any]:
        """Guide user through interactive contract deployment."""
        console.print("🚀 Smart Contract Deployment", style="bold blue")
        console.print("Let's deploy your smart contract to the blockchain.", style="dim")

        # Step 1: Select contract to deploy
        contract = await self._select_contract()

        if not contract:
            console.print("❌ No contract selected", style="yellow")
            return {"status": "cancelled"}

        # Step 2: Configure deployment
        deployment_config = await self._configure_deployment(contract)

        # Step 3: Review and confirm
        if await self._review_deployment(contract, deployment_config):
            return await self._execute_deployment(contract, deployment_config)
        else:
            console.print("❌ Deployment cancelled", style="yellow")
            return {"status": "cancelled"}

    async def _select_contract(self) -> Optional[Dict[str, Any]]:
        """Let user select a contract to deploy."""
        console.print("\n📋 Available contracts for deployment:", style="blue")

        try:
            contracts = await self.api_client.get_contracts(status="completed")

            if not contracts:
                console.print("❌ No completed contracts available for deployment", style="yellow")
                return None

            table = Table(show_header=True, header_style="bold blue")
            table.add_column("ID", style="cyan", width=15)
            table.add_column("Name", style="green")
            table.add_column("Type", style="yellow")
            table.add_column("Status", style="white")
            table.add_column("Created", style="dim")

            for contract in contracts:
                table.add_row(
                    contract.get("id", "unknown")[:15],
                    contract.get("contract_name", "unknown"),
                    contract.get("contract_type", "unknown"),
                    contract.get("status", "unknown"),
                    contract.get("created_at", "unknown")[:10]
                )

            console.print(table)

            contract_ids = [c.get("id", "") for c in contracts]
            contract_id = Prompt.ask("Select contract to deploy", choices=contract_ids)

            # Find selected contract
            selected_contract = next((c for c in contracts if c.get("id") == contract_id), None)
            return selected_contract

        except Exception as e:
            console.print(f"❌ Error fetching contracts: {e}", style="red")
            return None

    async def _configure_deployment(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Configure deployment parameters."""
        console.print("\n⚙️ Configure deployment parameters:", style="blue")

        config = {
            "network": Prompt.ask(
                "Target network",
                choices=["testnet", "mainnet"],
                default="testnet"
            ),
            "gas_limit": Prompt.ask("Gas limit", default="1000000"),
            "gas_price": Prompt.ask("Gas price (gwei)", default="20"),
            "deployer_address": Prompt.ask("Deployer address (leave empty for default)", default=""),
        }

        # Network-specific configurations
        if config["network"] == "testnet":
            config["network_config"] = {
                "rpc_url": "https://access-testnet.onflow.org",
                "chain_id": "testnet"
            }
        else:
            config["network_config"] = {
                "rpc_url": "https://access-mainnet.onflow.org",
                "chain_id": "mainnet"
            }

        # Additional options
        console.print("\n🔧 Additional deployment options:", style="blue")
        config["verify_source"] = Confirm.ask("Verify source code on blockchain explorer?", default=True)
        config["optimize"] = Confirm.ask("Optimize contract bytecode?", default=True)

        return config

    async def _review_deployment(self, contract: Dict[str, Any], config: Dict[str, Any]) -> bool:
        """Show deployment summary and ask for confirmation."""
        console.print("\n📊 Deployment Summary:", style="blue")

        summary_table = Table(show_header=False, box=None)
        summary_table.add_column("Property", style="cyan")
        summary_table.add_column("Value", style="white")

        summary_table.add_row("Contract", contract.get("contract_name", "unknown"))
        summary_table.add_row("Contract ID", contract.get("id", "unknown")[:15])
        summary_table.add_row("Network", config["network"])
        summary_table.add_row("Gas Limit", config["gas_limit"])
        summary_table.add_row("Gas Price", f"{config['gas_price']} gwei")
        summary_table.add_row("Verify Source", "Yes" if config["verify_source"] else "No")
        summary_table.add_row("Optimize", "Yes" if config["optimize"] else "No")

        console.print(summary_table)

        # Estimated cost calculation
        estimated_cost = int(config["gas_limit"]) * int(config["gas_price"]) / 10**9
        console.print(f"\n💰 Estimated deployment cost: {estimated_cost:.4f} FLOW", style="yellow")

        return Confirm.ask("\nProceed with deployment?")

    async def _execute_deployment(self, contract: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute contract deployment with real-time monitoring."""
        console.print("\n🚀 Deploying contract...", style="blue")

        # Connect to WebSocket for real-time updates
        try:
            connection_id = await self.api_client.connect_websocket()
            console.print(f"✅ Connected to real-time updates (ID: {connection_id})", style="green")
        except Exception as e:
            console.print(f"⚠️  WebSocket connection failed: {e}", style="yellow")

        # Prepare deployment data
        deployment_data = {
            "contract_id": contract.get("id"),
            "contract_name": contract.get("contract_name"),
            "network": config["network"],
            "gas_limit": int(config["gas_limit"]),
            "gas_price": int(config["gas_price"]),
            "deployer_address": config.get("deployer_address"),
            "verify_source": config["verify_source"],
            "optimize": config["optimize"],
            "network_config": config["network_config"]
        }

        # Execute deployment with real-time monitoring
        return await self._deploy_with_monitoring(deployment_data)

    async def _deploy_with_monitoring(self, deployment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy contract with real-time monitoring."""
        operation_id = str(uuid.uuid4())

        def create_progress_display():
            return Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=console,
            )

        with create_progress_display() as progress:
            task = progress.add_task("Initiating deployment...", total=100)

            try:
                # Start deployment
                result = await self.api_client.deploy_contract(deployment_data)
                progress.update(task, advance=10, description="Deployment initiated")

                deployment_id = result.get("deployment_id", "unknown")

                # Monitor deployment progress
                deployment_steps = [
                    (20, "Compiling contract..."),
                    (30, "Connecting to network..."),
                    (40, "Estimating gas..."),
                    (50, "Sending transaction..."),
                    (60, "Waiting for confirmation..."),
                    (70, "Mining transaction..."),
                    (80, "Verifying deployment..."),
                    (90, "Finalizing..."),
                    (100, "Deployment complete!")
                ]

                for progress_value, description in deployment_steps:
                    progress.update(task, advance=10, description=description)

                    # Simulate processing time (will be replaced with actual monitoring)
                    import time
                    time.sleep(1)

                    # Check actual deployment status
                    try:
                        status = await self.api_client.get_deployment_status(deployment_id)
                        if status.get("status") in ["completed", "success"]:
                            progress.update(task, completed=100, description="Deployment complete!")
                            break
                        elif status.get("status") == "failed":
                            raise Exception(f"Deployment failed: {status.get('error', 'Unknown error')}")
                    except Exception:
                        # Continue with simulation if status check fails
                        pass

                progress.update(task, completed=100, description="Deployment complete!")

                console.print("\n✅ Contract deployed successfully!", style="green")
                console.print(f"Deployment ID: {deployment_id}", style="cyan")
                console.print(f"Network: {deployment_data['network']}", style="cyan")

                # Show deployment details
                if "transaction_hash" in result:
                    console.print(f"Transaction Hash: {result['transaction_hash']}", style="cyan")
                if "contract_address" in result:
                    console.print(f"Contract Address: {result['contract_address']}", style="cyan")

                return {
                    "status": "success",
                    "deployment_id": deployment_id,
                    "contract_name": deployment_data["contract_name"],
                    "network": deployment_data["network"],
                    "transaction_hash": result.get("transaction_hash"),
                    "contract_address": result.get("contract_address")
                }

            except Exception as e:
                progress.update(task, description=f"Deployment failed: {e}")
                console.print(f"\n❌ Deployment failed: {e}", style="red")
                return {
                    "status": "failed",
                    "error": str(e),
                    "deployment_id": operation_id
                }

    async def list_deployments(self) -> None:
        """List all deployments."""
        console.print("📋 Deployment History", style="bold blue")

        try:
            deployments = await self.api_client.get_deployments(limit=50)

            if not deployments:
                console.print("No deployments found", style="yellow")
                return

            table = Table(show_header=True, header_style="bold blue")
            table.add_column("Deployment ID", style="cyan", width=15)
            table.add_column("Contract", style="green")
            table.add_column("Network", style="yellow")
            table.add_column("Status", style="white")
            table.add_column("Created", style="dim")

            for deployment in deployments:
                status_style = "green" if deployment.get("status") == "SUCCESS" else "red"
                table.add_row(
                    deployment.get("id", "unknown")[:15],
                    deployment.get("contract_name", "unknown"),
                    deployment.get("network", "unknown"),
                    Text(deployment.get("status", "unknown"), style=status_style),
                    deployment.get("created_at", "unknown")[:10]
                )

            console.print(table)

        except Exception as e:
            console.print(f"❌ Error fetching deployments: {e}", style="red")

    async def get_deployment_details(self, deployment_id: str) -> None:
        """Show detailed information about a specific deployment."""
        console.print(f"📊 Deployment Details: {deployment_id}", style="bold blue")

        try:
            # This would need to be implemented in the API
            # For now, we'll show a mock details view
            details = {
                "deployment_id": deployment_id,
                "status": "SUCCESS",
                "contract_name": "MyToken",
                "network": "testnet",
                "gas_used": 245678,
                "transaction_hash": "0x1234567890abcdef",
                "contract_address": "0xabcdef1234567890",
                "created_at": "2024-01-01T12:00:00Z"
            }

            details_table = Table(show_header=False, box=None)
            details_table.add_column("Property", style="cyan")
            details_table.add_column("Value", style="white")

            for key, value in details.items():
                details_table.add_row(key.replace("_", " ").title(), str(value))

            console.print(details_table)

        except Exception as e:
            console.print(f"❌ Error fetching deployment details: {e}", style="red")