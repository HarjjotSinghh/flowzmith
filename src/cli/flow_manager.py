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
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import uuid

import logging
logger = logging.getLogger(__name__)

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
            
            # Write the contract file
            contracts_dir = project_dir / "cadence" / "contracts"
            contracts_dir.mkdir(parents=True, exist_ok=True)
            
            contract_file = contracts_dir / f"{contract_name}.cdc"
            contract_file.write_text(contract_content, encoding="utf-8")
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
    
    async def deploy_contract(self, project_id: str, network: str = "emulator", 
                            account_name: str = "emulator-account") -> Dict[str, Any]:
        """Deploy contract to the specified network.
        
        Args:
            project_id: Project identifier
            network: Target network for deployment
            account_name: Account name to deploy to
            
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
                # Wait a bit for emulator to start
                await asyncio.sleep(3)
            
            # Deploy using flow project deploy
            deploy_cmd = ["flow", "project", "deploy", f"--network={network}"]
            deploy_result = await self._run_command(deploy_cmd, cwd=project_dir, timeout=120)
            
            # Stop emulator if we started it
            if emulator_process:
                await self._stop_emulator(emulator_process)
            
            if deploy_result.get("returncode") == 0:
                # Update metadata
                await self._update_project_metadata(project_dir, {
                    "deployed_at": datetime.now().isoformat(),
                    "deployment_network": network,
                    "deployment_status": "deployed"
                })
                
                logger.info("Contract deployed successfully: project_id=%s", project_id)
                return {
                    "status": "success",
                    "project_id": project_id,
                    "network": network,
                    "deployment_output": deploy_result.get("stdout", ""),
                    "deployed_at": datetime.now().isoformat()
                }
            else:
                error_msg = deploy_result.get("stderr", "Deployment failed")
                logger.error("Deployment failed for %s: %s", project_id, error_msg)
                return {
                    "status": "failed",
                    "error": error_msg,
                    "project_id": project_id
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
    
    async def _update_flow_config(self, project_dir: Path, contract_name: str, network: str):
        """Update flow.json configuration to include the contract."""
        flow_config_file = project_dir / "flow.json"
        
        if flow_config_file.exists():
            config = json.loads(flow_config_file.read_text(encoding="utf-8"))
        else:
            # Create basic config if it doesn't exist
            config = {
                "version": "1.0",
                "contracts": {},
                "networks": {
                    "emulator": "127.0.0.1:3569",
                    "testnet": "access.devnet.nodes.onflow.org:9000",
                    "mainnet": "access.mainnet.nodes.onflow.org:9000"
                },
                "accounts": {
                    "emulator-account": {
                        "address": "f8d6e0586b0a20c7",
                        "key": "ae1b44c0f5e8f6992ef2348898a35e50a8b0b9684000da8b1dade1b3bcd6ebee"
                    }
                },
                "deployments": {}
            }
        
        # Add contract
        config["contracts"][contract_name] = {
            "source": f"./cadence/contracts/{contract_name}.cdc",
            "aliases": {
                "testnet": "0x01",
                "mainnet": "0x01"
            }
        }
        
        # Ensure accounts section exists and has emulator-account for emulator network
        if "accounts" not in config:
            config["accounts"] = {}
        
        if network == "emulator" and "emulator-account" not in config["accounts"]:
            config["accounts"]["emulator-account"] = {
                "address": "f8d6e0586b0a20c7",
                "key": "ae1b44c0f5e8f6992ef2348898a35e50a8b0b9684000da8b1dade1b3bcd6ebee"
            }
        
        # Add deployment configuration
        if "deployments" not in config:
            config["deployments"] = {}
        
        if network not in config["deployments"]:
            config["deployments"][network] = {}
        
        # Use emulator-account for emulator, default for others
        account_name = "emulator-account" if network == "emulator" else "default"
        
        if account_name not in config["deployments"][network]:
            config["deployments"][network][account_name] = []
        
        if contract_name not in config["deployments"][network][account_name]:
            config["deployments"][network][account_name].append(contract_name)
        
        # Write updated config
        flow_config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")
        logger.info("Updated flow.json for contract %s", contract_name)
    
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
    
    async def _start_emulator(self, project_dir: Path) -> Optional[asyncio.subprocess.Process]:
        """Start Flow emulator for local deployment."""
        try:
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