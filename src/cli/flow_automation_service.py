"""
Flow CLI Automation Service for Flowzmith.

Handles the complete automated workflow:
1. Flow init in a new directory
2. Contract generation and file setup
3. MCP server generation
4. Automated deployment with account management
"""

import asyncio
import json
import uuid
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import logging
import os
from sqlalchemy.orm import Session

from .flow_manager import FlowProjectManager
from ..mcp_generator.mcp_server_generator import MCPServerGenerator
from ..mcp_generator.contract_analyzer import CadenceContractAnalyzer
from ..models.database import get_db
from ..models.deployment import DeploymentLog, DeploymentStatus
from ..models.contract import ContractSubmission
from ..models.generated_contract import GeneratedContract

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class FlowAutomationService:
    """Service for complete Flow CLI automation workflow."""
    
    def __init__(self, base_projects_dir: Path = None, db_session: Session = None):
        """Initialize the automation service.
        
        Args:
            base_projects_dir: Base directory for Flow projects
            db_session: Database session for storing deployment information
        """
        self.flow_manager = FlowProjectManager(base_projects_dir)
        self.mcp_generator = MCPServerGenerator()
        self.contract_analyzer = CadenceContractAnalyzer()
        self.db_session = db_session
        
        logger.info("FlowAutomationService initialized")
    
    async def initialize_flow_project(self, project_path: Path, contract_name: str, network: str = "testnet") -> Dict[str, Any]:
        """Initialize a Flow project using flow init command."""
        try:
            logger.info("Initializing Flow project at %s", project_path)
            
            # Ensure project directory exists
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Run flow init command
            result = await self._run_command(
                ["flow", "init", contract_name, "--network", network],
                cwd=project_path
            )
            
            if result["returncode"] == 0:
                logger.info("Flow project initialized successfully")
                return {
                    "status": "success",
                    "project_path": str(project_path),
                    "contract_name": contract_name,
                    "network": network,
                    "message": "Flow project initialized successfully"
                }
            else:
                logger.error("Flow init failed: %s", result.get("stderr"))
                return {
                    "status": "error",
                    "error": f"Flow init failed: {result.get('stderr')}",
                    "project_path": str(project_path)
                }
                
        except Exception as e:
            logger.error("Error initializing Flow project: %s", str(e))
            return {
                "status": "error",
                "error": str(e),
                "project_path": str(project_path)
            }
    
    async def execute_complete_workflow(
        self,
        contract_name: str,
        contract_content: str,
        network: str = "testnet",
        auto_deploy: bool = True,
        account_config: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Execute the complete automated workflow.
        
        Args:
            contract_name: Name of the contract
            contract_content: Cadence contract source code
            network: Target network (emulator, testnet, mainnet)
            auto_deploy: Whether to automatically deploy
            account_config: Optional account configuration with address/private_key
            
        Returns:
            Dict containing workflow results
        """
        workflow_id = str(uuid.uuid4())
        project_id = f"flow_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{workflow_id[:8]}"
        
        logger.info("Starting complete workflow: project_id=%s, contract=%s, network=%s", 
                   project_id, contract_name, network)
        
        workflow_result = {
            "workflow_id": workflow_id,
            "project_id": project_id,
            "contract_name": contract_name,
            "network": network,
            "started_at": datetime.now().isoformat(),
            "status": "initializing",
            "steps": {}
        }
        
        try:
            # Step 1: Check Flow CLI availability
            workflow_result["status"] = "checking_flow_cli"
            if not await self.flow_manager.check_flow_cli_installed():
                raise Exception("Flow CLI is not installed or not accessible")
            
            workflow_result["steps"]["flow_cli_check"] = {
                "status": "success",
                "completed_at": datetime.now().isoformat()
            }
            
            # Step 2: Create Flow project with flow init
            workflow_result["status"] = "creating_project"
            project_result = await self.flow_manager.create_flow_project(
                project_id=project_id,
                contract_name=contract_name,
                contract_content=contract_content,
                network=network
            )
            
            if project_result.get("status") != "success":
                raise Exception(f"Project creation failed: {project_result.get('error')}")
            
            workflow_result["steps"]["project_creation"] = {
                "status": "success",
                "project_dir": project_result.get("project_dir"),
                "completed_at": datetime.now().isoformat()
            }
            
            # Step 3: Generate MCP server
            workflow_result["status"] = "generating_mcp_server"
            mcp_result = await self._generate_mcp_server(
                project_id, contract_name, contract_content, network
            )
            
            workflow_result["steps"]["mcp_generation"] = {
                "status": "success" if mcp_result.get("success") else "failed",
                "files_generated": mcp_result.get("files", []),
                "mcp_dir": mcp_result.get("mcp_dir"),
                "completed_at": datetime.now().isoformat(),
                "error": mcp_result.get("error") if not mcp_result.get("success") else None
            }
            
            # Step 4: Setup account (if needed)
            if auto_deploy:
                workflow_result["status"] = "setting_up_account"
                account_result = await self._setup_deployment_account(
                    project_id, network, account_config
                )
                
                workflow_result["steps"]["account_setup"] = {
                    "status": "success" if account_result.get("success") else "failed",
                    "account_address": account_result.get("account_address"),
                    "account_name": account_result.get("account_name"),
                    "completed_at": datetime.now().isoformat(),
                    "error": account_result.get("error") if not account_result.get("success") else None
                }
                
                # Step 5: Deploy contract
                if account_result.get("success"):
                    workflow_result["status"] = "deploying_contract"
                    deploy_result = await self.flow_manager.deploy_contract(
                        project_id=project_id,
                        network=network,
                        account_name=account_result.get("account_name", "default")
                    )
                    
                    # Store deployment information in database
                    if self.db_session and deploy_result.get("status") == "success":
                        await self._store_deployment_info(
                            project_id=project_id,
                            deploy_result=deploy_result,
                            network=network,
                            contract_name=contract_name
                        )
                    
                    workflow_result["steps"]["deployment"] = {
                        "status": "success" if deploy_result.get("status") == "success" else "failed",
                        "transaction_hash": deploy_result.get("transaction_hash"),
                        "contract_address": deploy_result.get("contract_address"),
                        "account_address": deploy_result.get("account_address"),
                        "execution_time_ms": deploy_result.get("execution_time_ms"),
                        "completed_at": datetime.now().isoformat(),
                        "error": deploy_result.get("error") if deploy_result.get("status") != "success" else None
                    }
            
            # Final status
            workflow_result["status"] = "completed"
            workflow_result["completed_at"] = datetime.now().isoformat()
            
            logger.info("Workflow completed successfully: %s", workflow_id)
            return workflow_result
            
        except Exception as e:
            logger.exception("Workflow failed: %s", workflow_id)
            workflow_result["status"] = "failed"
            workflow_result["error"] = str(e)
            workflow_result["failed_at"] = datetime.now().isoformat()
            return workflow_result
    
    async def _generate_mcp_server(
        self,
        project_id: str,
        contract_name: str,
        contract_content: str,
        network: str
    ) -> Dict[str, Any]:
        """Generate MCP server for the contract.
        
        Args:
            project_id: Project identifier
            contract_name: Name of the contract
            contract_content: Contract source code
            network: Target network
            
        Returns:
            Dict containing generation result
        """
        try:
            project_dir = self.flow_manager.base_projects_dir / project_id
            mcp_dir = project_dir / "mcp_server"
            mcp_dir.mkdir(exist_ok=True)
            
            # Analyze contract
            contract_analysis = self.contract_analyzer.analyze_contract(
                contract_content, contract_name
            )
            
            # Generate MCP server files
            generated_files = self.mcp_generator.generate_mcp_server(
                contract_analysis=contract_analysis,
                contract_address="0x01",  # Placeholder, will be updated after deployment
                network=network,
                output_dir=mcp_dir
            )
            
            logger.info("MCP server generated for %s: %d files", project_id, len(generated_files))
            
            return {
                "success": True,
                "mcp_dir": str(mcp_dir),
                "files": list(generated_files.keys()),
                "contract_analysis": {
                    "functions": len(contract_analysis.functions),
                    "events": len(contract_analysis.events),
                    "resources": len(contract_analysis.resources)
                }
            }
            
        except Exception as e:
            logger.exception("MCP generation failed for %s", project_id)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _setup_deployment_account(
        self,
        project_id: str,
        network: str,
        account_config: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Setup account for deployment.
        
        Args:
            project_id: Project identifier
            network: Target network
            account_config: Optional account configuration
            
        Returns:
            Dict containing account setup result
        """
        try:
            project_dir = self.flow_manager.base_projects_dir / project_id
            
            if account_config and account_config.get("address") and account_config.get("private_key"):
                # Use provided account credentials
                account_name = f"{network}-account"
                await self._update_flow_json_with_account(
                    project_dir, account_name, account_config["address"], 
                    account_config["private_key"], network
                )
                
                logger.info("Using provided account for %s: %s", project_id, account_config["address"])
                return {
                    "success": True,
                    "account_address": account_config["address"],
                    "account_name": account_name,
                    "method": "provided_credentials"
                }
            
            elif network == "emulator":
                # Use emulator default account
                account_name = "emulator-account"
                await self._setup_emulator_account(project_dir, account_name)
                
                logger.info("Using emulator account for %s", project_id)
                return {
                    "success": True,
                    "account_address": "0xf8d6e0586b0a20c7",  # Default emulator account
                    "account_name": account_name,
                    "method": "emulator_default"
                }
            
            else:
                # Create new account using Flow CLI interactive mode
                account_result = await self._create_new_account(project_dir, network)
                
                if account_result.get("success"):
                    logger.info("Created new account for %s: %s", project_id, account_result.get("address"))
                    return {
                        "success": True,
                        "account_address": account_result.get("address"),
                        "account_name": account_result.get("name"),
                        "method": "flow_cli_create"
                    }
                else:
                    raise Exception(f"Account creation failed: {account_result.get('error')}")
            
        except Exception as e:
            logger.exception("Account setup failed for %s", project_id)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_new_account(self, project_dir: Path, network: str) -> Dict[str, Any]:
        """Create a new account using Flow CLI.
        
        Args:
            project_dir: Project directory
            network: Target network
            
        Returns:
            Dict containing account creation result
        """
        try:
            # Generate a unique account name
            account_name = f"{network}-account-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Use Flow CLI interactive account creation
            # This will prompt for account name and network selection
            create_cmd = ["flow", "accounts", "create", "--interactive"]
            
            # For non-interactive environments, we'll use manual mode with generated keys
            # First generate keys
            key_result = await self._run_command(
                ["flow", "keys", "generate"], cwd=project_dir
            )
            
            if key_result.get("returncode") != 0:
                raise Exception(f"Key generation failed: {key_result.get('stderr')}")
            
            # Parse the generated key from output
            key_output = key_result.get("stdout", "")
            # Extract public key from output (this is a simplified parser)
            public_key = None
            private_key = None
            
            for line in key_output.split('\n'):
                if 'Public Key' in line:
                    public_key = line.split(':')[-1].strip()
                elif 'Private Key' in line:
                    private_key = line.split(':')[-1].strip()
            
            if not public_key:
                raise Exception("Failed to extract public key from generation output")
            
            # For testnet/mainnet, we would need a funding account
            # For now, return the generated keys for manual setup
            return {
                "success": True,
                "address": "0x01",  # Placeholder - would be actual address after creation
                "name": account_name,
                "public_key": public_key,
                "private_key": private_key,
                "note": "Account keys generated. Manual funding required for testnet/mainnet."
            }
            
        except Exception as e:
            logger.exception("Account creation failed")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _setup_emulator_account(self, project_dir: Path, account_name: str):
        """Setup emulator account in flow.json.
        
        Args:
            project_dir: Project directory
            account_name: Account name to use
        """
        # Default emulator account configuration
        emulator_config = {
            "address": "0x" + os.getenv("FLOW_ACCOUNT_ADDRESS", "f8d6e0586b0a20c7"),
            "key": os.getenv("FLOW_PRIVATE_KEY", "2eae2f31cb5b756e50fa5d63a21867df3c9e1f8e8e1e1e1e1e1e1e1e1e1e1e1e")
        }
        
        await self._update_flow_json_with_account(
            project_dir, account_name, 
            emulator_config["address"], emulator_config["key"], "emulator"
        )
    
    async def _update_flow_json_with_account(
        self,
        project_dir: Path,
        account_name: str,
        address: str,
        private_key: str,
        network: str
    ):
        """Update flow.json with account configuration.
        
        Args:
            project_dir: Project directory
            account_name: Account name
            address: Account address
            private_key: Private key
            network: Network name
        """
        flow_json_path = project_dir / "flow.json"
        
        if flow_json_path.exists():
            flow_config = json.loads(flow_json_path.read_text())
        else:
            flow_config = {"version": "1.0"}
        
        # Update accounts section
        if "accounts" not in flow_config:
            flow_config["accounts"] = {}
        
        # Use detailed key format for testnet/mainnet, simple format for emulator
        if network in ["testnet", "mainnet"]:
            flow_config["accounts"][account_name] = {
                "address": address,
                "key": {
                    "type": "hex",
                    "index": 0,
                    "signatureAlgorithm": "ECDSA_secp256k1",
                    "hashAlgorithm": "SHA2_256",
                    "privateKey": private_key
                }
            }
        else:
            # For emulator, use simple format
            flow_config["accounts"][account_name] = {
                "address": address,
                "key": private_key
            }
        
        # Update deployments section
        if "deployments" not in flow_config:
            flow_config["deployments"] = {}
        
        if network not in flow_config["deployments"]:
            flow_config["deployments"][network] = {}
        
        # Add contract to deployment for this account
        contract_name = None
        if "contracts" in flow_config:
            contract_name = list(flow_config["contracts"].keys())[0]
        
        if contract_name:
            flow_config["deployments"][network][account_name] = [contract_name]
        
        # Write updated configuration
        flow_json_path.write_text(json.dumps(flow_config, indent=2))
        logger.info("Updated flow.json with account %s for %s", account_name, network)
    
    async def deploy_with_existing_account(
        self,
        project_path: str,
        contract_name: str,
        account_address: str,
        private_key: str,
        network: str = "testnet"
    ) -> Dict[str, Any]:
        """Deploy contract using existing account credentials.
        
        Args:
            project_path: Path to the project directory
            contract_name: Name of the contract to deploy
            account_address: Existing account address
            private_key: Private key for the account
            network: Target network (testnet, mainnet, emulator)
            
        Returns:
            Dict containing deployment result
        """
        try:
            project_dir = Path(project_path)
            
            # Setup account configuration
            account_config = {
                "address": account_address,
                "private_key": private_key
            }
            
            # Setup deployment account
            account_result = await self._setup_deployment_account(
                project_dir.name, network, account_config
            )
            
            if not account_result.get("success"):
                return {
                    "success": False,
                    "error": f"Account setup failed: {account_result.get('error')}"
                }
            
            # Deploy the contract
            deployment_result = await self._deploy_contract(
                project_dir, contract_name, account_result["account_name"], network
            )
            
            if deployment_result.get("success"):
                return {
                    "success": True,
                    "contract_address": deployment_result.get("contract_address"),
                    "account_address": account_address,
                    "network": network,
                    "transaction_id": deployment_result.get("transaction_id")
                }
            else:
                return {
                    "success": False,
                    "error": f"Deployment failed: {deployment_result.get('error')}"
                }
                
        except Exception as e:
            logger.exception("Deployment with existing account failed")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def deploy_with_new_account(
        self,
        project_path: str,
        contract_name: str,
        network: str = "testnet"
    ) -> Dict[str, Any]:
        """Deploy contract by creating a new account.
        
        Args:
            project_path: Path to the project directory
            contract_name: Name of the contract to deploy
            network: Target network (testnet, mainnet, emulator)
            
        Returns:
            Dict containing deployment result
        """
        try:
            project_dir = Path(project_path)
            
            # Setup deployment account (will create new one)
            account_result = await self._setup_deployment_account(
                project_dir.name, network
            )
            
            if not account_result.get("success"):
                return {
                    "success": False,
                    "error": f"Account creation failed: {account_result.get('error')}"
                }
            
            # Deploy the contract
            deployment_result = await self._deploy_contract(
                project_dir, contract_name, account_result["account_name"], network
            )
            
            if deployment_result.get("success"):
                return {
                    "success": True,
                    "contract_address": deployment_result.get("contract_address"),
                    "account_address": account_result.get("account_address"),
                    "network": network,
                    "transaction_id": deployment_result.get("transaction_id"),
                    "account_keys": {
                        "public_key": account_result.get("public_key"),
                        "private_key": account_result.get("private_key")
                    } if account_result.get("public_key") else None
                }
            else:
                return {
                    "success": False,
                    "error": f"Deployment failed: {deployment_result.get('error')}"
                }
                
        except Exception as e:
            logger.exception("Deployment with new account failed")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _deploy_contract(
        self,
        project_dir: Path,
        contract_name: str,
        account_name: str,
        network: str
    ) -> Dict[str, Any]:
        """Deploy contract to the specified network.
        
        Args:
            project_dir: Project directory
            contract_name: Contract name
            account_name: Account name to use for deployment
            network: Target network
            
        Returns:
            Dict containing deployment result
        """
        try:
            # Start emulator if needed
            if network == "emulator":
                emulator_result = await self._run_command(
                    ["flow", "emulator", "start", "--verbose"], 
                    cwd=project_dir,
                    timeout=30
                )
                
                if emulator_result.get("returncode") != 0:
                    logger.warning("Emulator start may have failed: %s", emulator_result.get("stderr"))
            
            # Deploy using Flow CLI
            deploy_cmd = [
                "flow", "project", "deploy",
                "--network", network
            ]
            
            deploy_result = await self._run_command(deploy_cmd, cwd=project_dir)
            
            if deploy_result.get("returncode") == 0:
                # Parse deployment output for contract address
                output = deploy_result.get("stdout", "")
                contract_address = self._extract_contract_address(output, contract_name)
                
                return {
                    "success": True,
                    "contract_address": contract_address,
                    "transaction_id": self._extract_transaction_id(output),
                    "output": output
                }
            else:
                return {
                    "success": False,
                    "error": deploy_result.get("stderr", "Unknown deployment error"),
                    "output": deploy_result.get("stdout", "")
                }
                
        except Exception as e:
            logger.exception("Contract deployment failed")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_contract_address(self, output: str, contract_name: str) -> Optional[str]:
        """Extract contract address from deployment output.
        
        Args:
            output: Deployment command output
            contract_name: Name of the deployed contract
            
        Returns:
            Contract address if found
        """
        # Look for patterns like "Contract deployed to 0x123..."
        import re
        
        patterns = [
            rf"{contract_name}.*deployed.*to\s+(0x[a-fA-F0-9]+)",
            r"Contract.*deployed.*to\s+(0x[a-fA-F0-9]+)",
            r"deployed.*to\s+(0x[a-fA-F0-9]+)",
            r"address:\s+(0x[a-fA-F0-9]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    async def _store_deployment_info(
        self,
        project_id: str,
        deploy_result: Dict[str, Any],
        network: str,
        contract_name: str
    ) -> None:
        """Store deployment information in the database.
        
        Args:
            project_id: Project identifier
            deploy_result: Deployment result from FlowProjectManager
            network: Target network
            contract_name: Name of the deployed contract
        """
        try:
            if not self.db_session:
                logger.warning("No database session available for storing deployment info")
                return
            
            # Create a deployment log entry
            deployment_log = DeploymentLog(
                submission_id=uuid.uuid4(),  # We'll need to link this properly later
                config_id=uuid.uuid4(),      # We'll need to link this properly later
                deployment_id=project_id,
                network=network,
                status=DeploymentStatus.SUCCESS if deploy_result.get("status") == "success" else DeploymentStatus.FAILED,
                error_message=deploy_result.get("error"),
                transaction_hash=deploy_result.get("transaction_hash"),
                execution_time_ms=deploy_result.get("execution_time_ms", 0),
                log_content=deploy_result.get("deployment_output", "")
            )
            
            self.db_session.add(deployment_log)
            self.db_session.commit()
            
            logger.info("Stored deployment info in database: project_id=%s, tx_hash=%s", 
                       project_id, deploy_result.get("transaction_hash"))
            
        except Exception as e:
            logger.error("Failed to store deployment info in database: %s", str(e))
            # Don't raise the exception to avoid breaking the deployment flow
    
    def _extract_transaction_id(self, output: str) -> Optional[str]:
        """Extract transaction ID from deployment output.
        
        Args:
            output: Deployment command output
            
        Returns:
            Transaction ID if found
        """
        import re
        
        patterns = [
            r"transaction\s+id:\s+([a-fA-F0-9]+)",
            r"tx\s+id:\s+([a-fA-F0-9]+)",
            r"Transaction\s+ID:\s+([a-fA-F0-9]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None

    async def _run_command(self, cmd: List[str], cwd: Path, timeout: int = 60) -> Dict[str, Any]:
        """Run a command and return result.
        
        Args:
            cmd: Command and arguments
            cwd: Working directory
            timeout: Command timeout in seconds
            
        Returns:
            Dict with returncode, stdout, stderr
        """
        logger.debug("Running command: %s (cwd=%s)", ' '.join(cmd), cwd)
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )
            
            return {
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore')
            }
            
        except asyncio.TimeoutError:
            logger.error("Command timeout: %s", ' '.join(cmd))
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timeout after {timeout} seconds"
            }
        except Exception as e:
            logger.exception("Command execution failed: %s", ' '.join(cmd))
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e)
            }