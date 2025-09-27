"""
Flow CLI Manager for Flowzmith.

Handles Flow CLI operations including project initialization, contract deployment,
and project management using the Flow CLI tool.
"""

import os
import json
import asyncio
import subprocess
import shutil
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import uuid

from dotenv import load_dotenv
load_dotenv()

import logging
logger = logging.getLogger(__name__)

# Import the markdown stripping function
from ..services.flow_service import strip_markdown_code_blocks

class FlowProjectManager:
    """Manages Flow CLI operations for contract projects."""
    
    def __init__(self, base_projects_dir: Path = None):
        """Initialize Flow project manager.
        
        Args:
            base_projects_dir: Base directory for Flow projects. Defaults to flow_projects/
        """
        if base_projects_dir is None:
            # Default to flow_projects directory in project root
            self.base_projects_dir = Path(__file__).parent.parent.parent / "flow_projects"
        else:
            self.base_projects_dir = Path(base_projects_dir)
        
        self.base_projects_dir.mkdir(exist_ok=True)
        logger.info("FlowProjectManager initialized with base_dir=%s", self.base_projects_dir)
    
    async def check_flow_cli_installed(self) -> bool:
        """Check if Flow CLI is installed and accessible."""
        try:
            result = await self._run_command(["flow", "version"], cwd=self.base_projects_dir)
            logger.info("Flow CLI version check: %s", result.get("stdout", "").strip())
            return result.get("returncode") == 0
        except Exception as e:
            logger.error("Flow CLI not found: %s", e)
            return False
    
    async def create_flow_project(self, project_id: str, contract_name: str, contract_content: str, 
                                network: str = "emulator") -> Dict[str, Any]:
        """Create a new Flow project with flow init and setup contract.
        
        Args:
            project_id: Unique identifier for the project
            contract_name: Name of the main contract
            contract_content: Cadence contract source code
            network: Target network (emulator, testnet, mainnet)
            
        Returns:
            Dict containing project info and status
        """
        project_dir = self.base_projects_dir / project_id
        logger.info("Creating Flow project: project_id=%s, contract=%s, network=%s", 
                   project_id, contract_name, network)
        
        try:
            # Create project directory
            project_dir.mkdir(exist_ok=True)
            
            # Run flow init in the project directory
            init_result = await self._run_command(["flow", "init"], cwd=project_dir)
            if init_result.get("returncode") != 0:
                raise Exception(f"Flow init failed: {init_result.get('stderr', 'Unknown error')}")
            
            logger.info("Flow init completed for project %s", project_id)
            
            # Generate proper keys and fix flow.json configuration
            await self._setup_flow_config_with_keys(project_dir, network)
            
            # Write the contract file
            contracts_dir = project_dir / "contracts"
            contracts_dir.mkdir(parents=True, exist_ok=True)
            
            # Strip markdown code blocks from contract content before writing
            clean_contract_content = strip_markdown_code_blocks(contract_content)
            
            contract_file = contracts_dir / f"{contract_name}.cdc"
            contract_file.write_text(clean_contract_content, encoding="utf-8")
            logger.info("Contract file written: %s", contract_file)
            
            # Update flow.json to include the contract
            await self._update_flow_config(project_dir, contract_name, network)
            
            # Create metadata file
            metadata = {
                "project_id": project_id,
                "contract_name": contract_name,
                "network": network,
                "created_at": datetime.now().isoformat(),
                "status": "initialized"
            }
            
            metadata_file = project_dir / "metadata.json"
            metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
            
            # Create README
            await self._create_project_readme(project_dir, contract_name, project_id)
            
            logger.info("Flow project created successfully: %s", project_id)
            return {
                "status": "success",
                "project_id": project_id,
                "project_dir": str(project_dir),
                "contract_name": contract_name,
                "network": network,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.exception("Failed to create Flow project %s", project_id)
            # Cleanup on failure
            if project_dir.exists():
                shutil.rmtree(project_dir, ignore_errors=True)
            return {
                "status": "failed",
                "error": str(e),
                "project_id": project_id
            }

    async def _setup_flow_config_with_keys(self, project_dir: Path, network: str):
        """Setup flow.json with proper keys and account configuration."""
        flow_config_file = project_dir / "flow.json"
        
        try:
            # Generate new keys using Flow CLI
            key_result = await self._run_command(["flow", "keys", "generate"], cwd=project_dir)
            if key_result.get("returncode") != 0:
                raise Exception(f"Key generation failed: {key_result.get('stderr')}")
            
            # Parse the key generation output
            key_output = key_result.get("stdout", "")
            private_key = None
            public_key = None
            
            for line in key_output.split('\n'):
                if 'Private Key' in line and ':' in line:
                    private_key = line.split(':', 1)[1].strip()
                elif 'Public Key' in line and ':' in line:
                    public_key = line.split(':', 1)[1].strip()
            
            if not private_key or not public_key:
                # Fallback to parsing different output format
                lines = key_output.strip().split('\n')
                for i, line in enumerate(lines):
                    if 'private key' in line.lower() and i + 1 < len(lines):
                        private_key = lines[i + 1].strip()
                    elif 'public key' in line.lower() and i + 1 < len(lines):
                        public_key = lines[i + 1].strip()
            
            if not private_key:
                logger.warning("Could not parse generated private key, using fallback")
                # Use a known valid emulator key as fallback
                private_key = "ae1b44c0f5e8f6992ef2348898a35e50a8b0b9684000da8b1dade1b3bcd6ebee"
                public_key = "f8d6e0586b0a20c7"
            
            logger.info("Generated keys for project, private_key length: %d", len(private_key) if private_key else 0)
            
            # Read existing flow.json
            if flow_config_file.exists():
                config = json.loads(flow_config_file.read_text(encoding="utf-8"))
            else:
                config = {}
            
            # Setup proper configuration based on network
            if network == "emulator":
                # For emulator, use a consistent key across all projects to avoid conflicts
                # Use the default emulator service account key
                emulator_private_key = "ae1b44c0f5e8f6992ef2348898a35e50a8b0b9684000da8b1dade1b3bcd6ebee"
                
                config.update({
                    "networks": {
                        "emulator": "127.0.0.1:3569",
                        "testnet": "access.devnet.nodes.onflow.org:9000",
                        "mainnet": "access.mainnet.nodes.onflow.org:9000"
                    },
                    "accounts": {
                        "emulator-account": {
                            "address": "service",
                            "key": {
                                "type": "file",
                                "location": "./emulator-account.pkey"
                            }
                        }
                    },
                    "deployments": {},
                    "contracts": {}
                })
                
                # Write the consistent private key to the key file
                key_file = project_dir / "emulator-account.pkey"
                key_file.write_text(f"0x{emulator_private_key}", encoding="utf-8")
                logger.info("Created emulator key file with consistent key: %s", key_file)
            else:
                # For testnet/mainnet, use credentials from environment variables
                flow_account_address = os.getenv("FLOW_ACCOUNT_ADDRESS")
                flow_private_key = os.getenv("FLOW_PRIVATE_KEY")
                
                if not flow_account_address or not flow_private_key:
                    logger.error("Missing testnet credentials in environment variables")
                    raise ValueError("FLOW_ACCOUNT_ADDRESS and FLOW_PRIVATE_KEY must be set for testnet deployment")
                
                config.update({
                    "networks": {
                        "emulator": "127.0.0.1:3569",
                        "testnet": "access.devnet.nodes.onflow.org:9000",
                        "mainnet": "access.mainnet.nodes.onflow.org:9000"
                    },
                    "accounts": {
                        "testnet-account": {
                            "address": flow_account_address,
                            "key": {
                                "type": "hex",
                                "index": 0,
                                "signatureAlgorithm": "ECDSA_secp256k1",
                                "hashAlgorithm": "SHA2_256",
                                "privateKey": flow_private_key
                            }
                        }
                    },
                    "deployments": {},
                    "contracts": {}
                })
            
            # Write the updated configuration
            flow_config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")
            logger.info("Updated flow.json with proper keys for network: %s", network)
            
        except Exception as e:
            logger.error("Failed to setup flow config with keys: %s", str(e))
            # Create a basic working configuration as fallback
            await self._create_fallback_flow_config(project_dir, network)

    async def _create_fallback_flow_config(self, project_dir: Path, network: str):
        """Create a fallback flow.json configuration that works."""
        flow_config_file = project_dir / "flow.json"
        
        if network == "emulator":
            # Use the known working emulator service account
            config = {
                "networks": {
                    "emulator": "127.0.0.1:3569",
                    "testnet": "access.devnet.nodes.onflow.org:9000",
                    "mainnet": "access.mainnet.nodes.onflow.org:9000"
                },
                "accounts": {
                    "emulator-account": {
                        "address": "service",
                        "key": "ae1b44c0f5e8f6992ef2348898a35e50a8b0b9684000da8b1dade1b3bcd6ebee"
                    }
                },
                "deployments": {},
                "contracts": {}
            }
        else:
            # For testnet/mainnet, use credentials from environment variables
            flow_account_address = os.getenv("FLOW_ACCOUNT_ADDRESS")
            flow_private_key = os.getenv("FLOW_PRIVATE_KEY")
            
            accounts = {}
            if flow_account_address and flow_private_key:
                accounts["testnet-account"] = {
                    "address": flow_account_address,
                    "key": {
                        "type": "hex",
                        "index": 0,
                        "signatureAlgorithm": "ECDSA_secp256k1",
                        "hashAlgorithm": "SHA2_256",
                        "privateKey": flow_private_key
                    }
                }
            
            config = {
                "networks": {
                    "emulator": "127.0.0.1:3569",
                    "testnet": "access.devnet.nodes.onflow.org:9000",
                    "mainnet": "access.mainnet.nodes.onflow.org:9000"
                },
                "accounts": accounts,
                "deployments": {},
                "contracts": {}
            }
        
        flow_config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")
        logger.info("Created fallback flow.json configuration for network: %s", network)

    async def deploy_contract(self, project_id: str, network: str = "emulator", 
                            account_name: str = "emulator-account", update: bool = False) -> Dict[str, Any]:
        """Deploy contract to the specified network.
        
        Args:
            project_id: Project identifier
            network: Target network for deployment
            account_name: Account name to deploy to
            update: Whether to force update existing contracts
            
        Returns:
            Dict containing deployment result
        """
        project_dir = self.base_projects_dir / project_id
        logger.info("Deploying contract: project_id=%s, network=%s, account=%s", 
                   project_id, network, account_name)
        
        if not project_dir.exists():
            return {
                "status": "failed",
                "error": f"Project {project_id} not found"
            }
        
        try:
            # Start emulator if deploying to emulator
            emulator_process = None
            if network == "emulator":
                emulator_process = await self._start_emulator(project_dir)
                # Only wait if we actually started a new emulator
                if emulator_process:
                    await asyncio.sleep(3)
            
            # Deploy using flow project deploy
            deploy_cmd = ["flow", "project", "deploy", f"--network={network}"]
            if update:
                deploy_cmd.append("--update")
            start_time = datetime.now()
            deploy_result = await self._run_command(deploy_cmd, cwd=project_dir, timeout=120)
            end_time = datetime.now()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Stop emulator if we started it
            if emulator_process:
                await self._stop_emulator(emulator_process)
            
            if deploy_result.get("returncode") == 0:
                # Parse deployment output for transaction hash and contract address
                deployment_output = deploy_result.get("stdout", "")
                deployment_info = self._parse_deployment_output(deployment_output)
                
                # Update metadata
                await self._update_project_metadata(project_dir, {
                    "deployed_at": datetime.now().isoformat(),
                    "deployment_network": network,
                    "deployment_status": "deployed",
                    "transaction_hash": deployment_info.get("transaction_hash"),
                    "contract_address": deployment_info.get("contract_address")
                })
                
                logger.info("Contract deployed successfully: project_id=%s, tx_hash=%s", 
                           project_id, deployment_info.get("transaction_hash"))
                return {
                    "status": "success",
                    "project_id": project_id,
                    "network": network,
                    "deployment_output": deployment_output,
                    "transaction_hash": deployment_info.get("transaction_hash"),
                    "contract_address": deployment_info.get("contract_address"),
                    "account_address": deployment_info.get("account_address"),
                    "execution_time_ms": execution_time_ms,
                    "deployed_at": datetime.now().isoformat()
                }
            else:
                error_msg = deploy_result.get("stderr", "Deployment failed")
                logger.error("Deployment failed for %s: %s", project_id, error_msg)
                return {
                    "status": "failed",
                    "error": error_msg,
                    "project_id": project_id,
                    "execution_time_ms": execution_time_ms
                }
                
        except Exception as e:
            logger.exception("Deployment error for project %s", project_id)
            return {
                "status": "failed",
                "error": str(e),
                "project_id": project_id
            }
    
    async def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get status and information about a Flow project.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Dict containing project status and metadata
        """
        project_dir = self.base_projects_dir / project_id
        
        if not project_dir.exists():
            return {
                "status": "not_found",
                "project_id": project_id
            }
        
        try:
            # Read metadata
            metadata_file = project_dir / "metadata.json"
            metadata = {}
            if metadata_file.exists():
                metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
            
            # Check flow.json
            flow_config_file = project_dir / "flow.json"
            flow_config = {}
            if flow_config_file.exists():
                flow_config = json.loads(flow_config_file.read_text(encoding="utf-8"))
            
            # List contract files with details
            contracts_dir = project_dir / "cadence" / "contracts"
            contract_files = []
            contracts_info = []
            if contracts_dir.exists():
                for contract_file in contracts_dir.glob("*.cdc"):
                    contract_files.append(contract_file.name)
                    contracts_info.append({
                        "name": contract_file.stem,
                        "filename": contract_file.name,
                        "path": str(contract_file),
                        "size": contract_file.stat().st_size if contract_file.exists() else 0
                    })
            
            # Extract name from metadata or use project_id as fallback
            project_name = metadata.get("name", project_id)
            
            return {
                "status": "found",
                "project_id": project_id,
                "name": project_name,
                "path": str(project_dir),
                "project_dir": str(project_dir),
                "metadata": metadata,
                "flow_config": flow_config,
                "contract_files": contract_files,
                "has_flow_json": flow_config_file.exists(),
                "has_contracts": len(contract_files) > 0,
                "network": metadata.get("network", "emulator"),
                "contracts": contracts_info
            }
            
        except Exception as e:
            logger.exception("Error getting project status for %s", project_id)
            return {
                "status": "error",
                "error": str(e),
                "project_id": project_id
            }
    
    async def list_projects(self) -> List[Dict[str, Any]]:
        """List all Flow projects.
        
        Returns:
            List of project information dictionaries
        """
        projects = []
        
        try:
            for project_dir in self.base_projects_dir.iterdir():
                if project_dir.is_dir() and not project_dir.name.startswith('.'):
                    project_status = await self.get_project_status(project_dir.name)
                    if project_status.get("status") != "not_found":
                        projects.append(project_status)
            
            logger.info("Listed %d Flow projects", len(projects))
            return projects
            
        except Exception as e:
            logger.exception("Error listing projects")
            return []
    
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
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            
            result = {
                "returncode": process.returncode,
                "stdout": stdout.decode("utf-8", errors="ignore"),
                "stderr": stderr.decode("utf-8", errors="ignore")
            }
            
            logger.debug("Command result: returncode=%d", process.returncode)
            return result
            
        except asyncio.TimeoutError:
            logger.error("Command timeout: %s", ' '.join(cmd))
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timeout"
            }
        except Exception as e:
            logger.exception("Command execution failed: %s", ' '.join(cmd))
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e)
            }
    
    def _parse_deployment_output(self, output: str) -> Dict[str, Any]:
        """Parse Flow CLI deployment output to extract transaction hash and other info.
        
        Args:
            output: Raw output from flow project deploy command
            
        Returns:
            Dict containing parsed deployment information
        """
        deployment_info = {
            "transaction_hash": None,
            "contract_address": None,
            "account_address": None
        }
        
        try:
            # Common patterns in Flow CLI output
            # Transaction ID pattern: "Transaction ID: 0x..."
            tx_pattern = r"Transaction ID:\s*(0x[0-9a-fA-F]+)"
            tx_match = re.search(tx_pattern, output)
            if tx_match:
                deployment_info["transaction_hash"] = tx_match.group(1)
            
            # Alternative transaction hash patterns
            tx_patterns = [
                r"tx_id:\s*(0x[0-9a-fA-F]+)",
                r"transaction_id:\s*(0x[0-9a-fA-F]+)",
                r"Transaction:\s*(0x[0-9a-fA-F]+)",
                r"(0x[0-9a-fA-F]{64})"  # 64-char hex string with 0x prefix
            ]
            
            for pattern in tx_patterns:
                if not deployment_info["transaction_hash"]:
                    match = re.search(pattern, output, re.IGNORECASE)
                    if match:
                        deployment_info["transaction_hash"] = match.group(1)
                        break
            
            # Contract address patterns
            # Pattern 1: "Contract deployed at: 0x..."
            addr_pattern = r"Contract deployed at:\s*(0x[0-9a-fA-F]+)"
            addr_match = re.search(addr_pattern, output)
            if addr_match:
                deployment_info["contract_address"] = addr_match.group(1)
            
            # Pattern 2: "ContractName -> 0x... (transaction_hash) [status]" (most common format)
            if not deployment_info["contract_address"]:
                # This pattern captures: ContractName -> 0xAddress (TransactionHash) [status]
                contract_deploy_pattern = r"(\w+)\s*->\s*(0x[0-9a-fA-F]+)\s*\(([0-9a-fA-F]+)\)"
                contract_match = re.search(contract_deploy_pattern, output)
                if contract_match:
                    deployment_info["contract_address"] = contract_match.group(2)
                    deployment_info["transaction_hash"] = "0x" + contract_match.group(3)
                    deployment_info["account_address"] = contract_match.group(2)  # Same as contract address for emulator
                else:
                    # Fallback to simpler pattern without transaction hash
                    simple_pattern = r"\w+\s*->\s*(0x[0-9a-fA-F]+)"
                    simple_match = re.search(simple_pattern, output)
                    if simple_match:
                        deployment_info["contract_address"] = simple_match.group(1)
                        deployment_info["account_address"] = simple_match.group(1)
            
            # Account address pattern: "Account: 0x..."
            account_pattern = r"Account:\s*(0x[0-9a-fA-F]+)"
            account_match = re.search(account_pattern, output)
            if account_match:
                deployment_info["account_address"] = account_match.group(1)
            
            # Alternative account patterns
            account_patterns = [
                r"Deploying to account:\s*(0x[0-9a-fA-F]+)",
                r"Using account:\s*(0x[0-9a-fA-F]+)",
                r"Account address:\s*(0x[0-9a-fA-F]+)"
            ]
            
            for pattern in account_patterns:
                if not deployment_info["account_address"]:
                    match = re.search(pattern, output, re.IGNORECASE)
                    if match:
                        deployment_info["account_address"] = match.group(1)
                        break
            
            logger.debug("Parsed deployment info: %s", deployment_info)
            
        except Exception as e:
            logger.warning("Failed to parse deployment output: %s", str(e))
        
        return deployment_info
    
    async def _update_flow_config(self, project_dir: Path, contract_name: str, network: str):
        """Update flow.json configuration to include the contract."""
        flow_config_file = project_dir / "flow.json"
        
        if flow_config_file.exists():
            config = json.loads(flow_config_file.read_text(encoding="utf-8"))
        else:
            # This should not happen as flow.json should already be properly configured
            logger.warning("flow.json not found, creating basic config for network: %s", network)
            await self._create_fallback_flow_config(project_dir, network)
            config = json.loads(flow_config_file.read_text(encoding="utf-8"))
        
        # Add contract to contracts section
        if "contracts" not in config:
            config["contracts"] = {}
            
        # Set contract configuration with proper format
        config["contracts"][contract_name] = {
            "source": f"./contracts/{contract_name}.cdc",
            "aliases": {
                "emulator": "0xf8d6e0586b0a20c7",
                "testnet": "0x01",
                "mainnet": "0x01"
            }
        }
        
        # Ensure deployments section exists
        if "deployments" not in config:
            config["deployments"] = {}
        
        # Add deployment configuration for the specific network
        if network not in config["deployments"]:
            config["deployments"][network] = {}
        
        # Use appropriate account name based on network and existing accounts
        account_name = None
        if network == "emulator" and "emulator-account" in config.get("accounts", {}):
            account_name = "emulator-account"
        elif network == "testnet" and "testnet-account" in config.get("accounts", {}):
            account_name = "testnet-account"
        elif "default" in config.get("accounts", {}):
            account_name = "default"
        elif config.get("accounts"):
            # Use the first available account
            account_name = list(config["accounts"].keys())[0]
        else:
            # No accounts configured, use default names
            if network == "emulator":
                account_name = "emulator-account"
            elif network == "testnet":
                account_name = "testnet-account"
            else:
                account_name = "default"
        
        if account_name not in config["deployments"][network]:
            config["deployments"][network][account_name] = []
        
        # Add contract to deployment if not already present
        if contract_name not in config["deployments"][network][account_name]:
            config["deployments"][network][account_name].append(contract_name)
        
        # Write updated config
        flow_config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")
        logger.info("Updated flow.json for contract %s on network %s using account %s", 
                   contract_name, network, account_name)
    
    async def _create_project_readme(self, project_dir: Path, contract_name: str, project_id: str):
        """Create a README file for the project."""
        readme_content = f"""# {contract_name} Contract

This is a Flow blockchain smart contract project generated by Flowzmith.

## Project Information
- **Project ID**: {project_id}
- **Contract Name**: {contract_name}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Project Structure
```
{project_id}/
├── flow.json              # Flow project configuration
├── metadata.json          # Project metadata
├── README.md             # This file
└── cadence/
    ├── contracts/        # Smart contracts
    ├── scripts/          # Read-only scripts
    ├── transactions/     # State-changing transactions
    └── tests/           # Contract tests
```

## Getting Started

### Prerequisites
- [Flow CLI](https://docs.onflow.org/flow-cli/install/) installed

### Deploy to Emulator
```bash
# Start the Flow emulator
flow emulator

# In another terminal, deploy the contract
flow project deploy --network=emulator
```

### Deploy to Testnet
```bash
# Deploy to testnet (requires testnet account configuration)
flow project deploy --network=testnet
```

## Contract Files
- `cadence/contracts/{contract_name}.cdc` - Main contract implementation

## Learn More
- [Flow Documentation](https://docs.onflow.org/)
- [Cadence Language Reference](https://docs.onflow.org/cadence/)
- [Flow CLI Documentation](https://docs.onflow.org/flow-cli/)
"""
        
        readme_file = project_dir / "README.md"
        readme_file.write_text(readme_content, encoding="utf-8")
        logger.info("Created README for project %s", project_id)
    
    async def deploy_contracts(self, project_name: str, network: str = "emulator", 
                             contract_name: Optional[str] = None) -> Dict[str, Any]:
        """Deploy contracts in a Flow project using flow project deploy.
        
        Args:
            project_name: Name of the project to deploy
            network: Target network (emulator, testnet, mainnet)
            contract_name: Specific contract to deploy (optional)
            
        Returns:
            Dict containing deployment result
        """
        project_dir = self.base_projects_dir / project_name
        logger.info("Deploying contracts: project=%s, network=%s, contract=%s", 
                   project_name, network, contract_name)
        
        try:
            if not project_dir.exists():
                raise Exception(f"Project directory not found: {project_dir}")
            
            # Check if flow.json exists
            flow_config_file = project_dir / "flow.json"
            if not flow_config_file.exists():
                raise Exception(f"flow.json not found in project: {project_name}")
            
            # Build deployment command
            deploy_cmd = ["flow", "project", "deploy", f"--network={network}"]
            
            # Note: Flow CLI deploys all contracts in flow.json, cannot specify individual contracts
            
            # Run deployment command
            result = await self._run_command(deploy_cmd, cwd=project_dir)
            
            if result.get("returncode") == 0:
                logger.info("Contract deployment successful for project %s", project_name)
                return {
                    "success": True,
                    "project_name": project_name,
                    "network": network,
                    "contract_name": contract_name,
                    "transaction_hash": self._extract_transaction_hash(result.get("stdout", "")),
                    "output": result.get("stdout", "")
                }
            else:
                error_msg = result.get("stderr", "Unknown deployment error")
                logger.error("Contract deployment failed for project %s: %s", project_name, error_msg)
                return {
                    "success": False,
                    "project_name": project_name,
                    "network": network,
                    "contract_name": contract_name,
                    "error": error_msg,
                    "output": result.get("stdout", "")
                }
                
        except Exception as e:
            logger.exception("Error deploying contracts for project %s", project_name)
            return {
                "success": False,
                "project_name": project_name,
                "network": network,
                "contract_name": contract_name,
                "error": str(e)
            }

    def _extract_transaction_hash(self, output: str) -> Optional[str]:
        """Extract transaction hash from Flow CLI output.
        
        Args:
            output: CLI output string
            
        Returns:
            Transaction hash if found, None otherwise
        """
        import re
        # Look for transaction hash patterns in the output
        hash_patterns = [
            r"Transaction ID: ([a-fA-F0-9]+)",
            r"transaction hash: ([a-fA-F0-9]+)",
            r"Transaction: ([a-fA-F0-9]+)"
        ]
        
        for pattern in hash_patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None

    async def _update_project_metadata(self, project_dir: Path, updates: Dict[str, Any]):
        """Update project metadata file."""
        metadata_file = project_dir / "metadata.json"
        
        metadata = {}
        if metadata_file.exists():
            metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
        
        metadata.update(updates)
        metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        logger.debug("Updated metadata for project in %s", project_dir)
    
    async def _is_emulator_running(self) -> bool:
        """Check if Flow emulator is already running by testing connection to default port."""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', 3569))
            sock.close()
            return result == 0
        except Exception:
            return False

    async def _start_emulator(self, project_dir: Path) -> Optional[asyncio.subprocess.Process]:
        """Start Flow emulator for local deployment."""
        try:
            # Check if emulator is already running
            if await self._is_emulator_running():
                logger.info("Flow emulator is already running, skipping start")
                return None
                
            logger.info("Starting Flow emulator for project in %s", project_dir)
            process = await asyncio.create_subprocess_exec(
                "flow", "emulator",
                cwd=project_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            return process
        except Exception as e:
            logger.error("Failed to start emulator: %s", e)
            return None
    
    async def _stop_emulator(self, process: asyncio.subprocess.Process):
        """Stop Flow emulator process."""
        try:
            process.terminate()
            await asyncio.wait_for(process.wait(), timeout=10)
            logger.info("Flow emulator stopped")
        except Exception as e:
            logger.error("Error stopping emulator: %s", e)
            try:
                process.kill()
            except Exception:
                pass