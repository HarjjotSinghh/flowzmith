"""
Flow blockchain CLI integration service.
"""

import os
import json
import subprocess
import tempfile
import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from enum import Enum
from sqlalchemy.orm import Session
from datetime import datetime

from ..models import (
    ContractSubmission,
    GeneratedConfiguration,
    DeploymentLog,
    DeploymentStatus,
    TransactionProposal,
    TransactionType,
    ApprovalStatus
)
from ..config import get_settings

logger = logging.getLogger(__name__)


class FlowNetwork(str, Enum):
    """Supported Flow networks."""
    TESTNET = "testnet"
    MAINNET = "mainnet"
    EMULATOR = "emulator"


class FlowService:
    """Service for Flow blockchain operations."""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.settings = get_settings()
        self._validate_flow_cli()

    def _validate_flow_cli(self):
        """Validate Flow CLI installation."""
        try:
            result = subprocess.run(
                ["flow", "version"],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Flow CLI version: {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Flow CLI not found or not working: {e}")
            raise RuntimeError("Flow CLI is required but not installed or not in PATH")

    def create_project_structure(self, submission_id: str) -> Path:
        """Create Flow project structure for a submission."""
        project_path = Path(self.settings.flow_projects_path) / submission_id
        project_path.mkdir(parents=True, exist_ok=True)

        # Create required directories
        (project_path / "contracts").mkdir(exist_ok=True)
        (project_path / "transactions").mkdir(exist_ok=True)
        (project_path / "scripts").mkdir(exist_ok=True)

        return project_path

    def save_contract_files(
        self,
        project_path: Path,
        contract_code: str,
        config: Dict[str, Any]
    ) -> Tuple[str, str]:
        """Save contract and configuration files."""
        # Save contract code
        contract_name = config.get("contracts", {}).get("default") or "SmartContract"
        contract_file = project_path / "contracts" / f"{contract_name}.cdc"

        with open(contract_file, 'w') as f:
            f.write(contract_code)

        # Save flow.json configuration
        config_file = project_path / "flow.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        return str(contract_file), str(config_file)

    async def deploy_contract(
        self,
        generated_config: GeneratedConfiguration,
        network: FlowNetwork = FlowNetwork.TESTNET
    ) -> DeploymentLog:
        """Deploy a contract to Flow blockchain."""
        try:
            # Update submission status
            generated_config.contract_submission.status = "PROCESSING"
            self.db_session.commit()

            # Create project structure
            project_path = self.create_project_structure(str(generated_config.submission_id))

            # Save files
            contract_file, config_file = self.save_contract_files(
                project_path,
                generated_config.generated_contract_code,
                generated_config.config_content
            )

            # Deploy contract
            deployment_result = await self._execute_deployment(
                project_path,
                network,
                contract_file
            )

            # Create deployment log
            deployment_log = DeploymentLog(
                submission_id=generated_config.submission_id,
                config_id=generated_config.id,
                deployment_id=deployment_result.get("deployment_id"),
                network=network.value,
                status=deployment_result["status"],
                error_message=deployment_result.get("error_message"),
                error_code=deployment_result.get("error_code"),
                transaction_hash=deployment_result.get("transaction_hash"),
                gas_used=deployment_result.get("gas_used"),
                execution_time_ms=deployment_result["execution_time_ms"],
                log_content=deployment_result["log_content"]
            )

            self.db_session.add(deployment_log)
            self.db_session.commit()

            # Update submission status based on deployment result
            if deployment_result["status"] == DeploymentStatus.SUCCESS:
                generated_config.contract_submission.status = "COMPLETED"
            else:
                generated_config.contract_submission.status = "FAILED"

            self.db_session.commit()

            logger.info(f"Contract deployment completed for submission {generated_config.submission_id}")

            return deployment_log

        except Exception as e:
            logger.error(f"Contract deployment failed for config {generated_config.id}: {e}")

            # Create failed deployment log
            deployment_log = DeploymentLog(
                submission_id=generated_config.submission_id,
                config_id=generated_config.id,
                network=network.value,
                status=DeploymentStatus.FAILED,
                error_message=str(e),
                execution_time_ms=0,
                log_content=f"Deployment failed: {str(e)}"
            )

            self.db_session.add(deployment_log)
            self.db_session.commit()

            # Update submission status
            generated_config.contract_submission.status = "FAILED"
            self.db_session.commit()

            return deployment_log

    async def _execute_deployment(
        self,
        project_path: Path,
        network: FlowNetwork,
        contract_file: str
    ) -> Dict[str, Any]:
        """Execute contract deployment using Flow CLI."""
        import time
        start_time = time.time()

        try:
            # Change to project directory
            os.chdir(project_path)

            # Run deployment command
            cmd = [
                "flow", "project", "deploy",
                "--network", network.value,
                "--update",
                "--filter", "contracts"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            execution_time_ms = int((time.time() - start_time) * 1000)

            if result.returncode == 0:
                # Extract transaction hash from output
                transaction_hash = self._extract_transaction_hash(result.stdout)

                return {
                    "status": DeploymentStatus.SUCCESS,
                    "transaction_hash": transaction_hash,
                    "execution_time_ms": execution_time_ms,
                    "log_content": result.stdout,
                    "deployment_id": f"deploy_{int(time.time())}"
                }
            else:
                # Parse error
                error_info = self._parse_deployment_error(result.stderr)

                return {
                    "status": DeploymentStatus.FAILED,
                    "error_message": error_info["message"],
                    "error_code": error_info["code"],
                    "execution_time_ms": execution_time_ms,
                    "log_content": f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
                }

        except subprocess.TimeoutExpired:
            return {
                "status": DeploymentStatus.TIMEOUT,
                "error_message": "Deployment timed out after 5 minutes",
                "execution_time_ms": int((time.time() - start_time) * 1000),
                "log_content": "Deployment timed out"
            }
        except Exception as e:
            return {
                "status": DeploymentStatus.FAILED,
                "error_message": str(e),
                "execution_time_ms": int((time.time() - start_time) * 1000),
                "log_content": f"Deployment failed: {str(e)}"
            }

    def _extract_transaction_hash(self, output: str) -> Optional[str]:
        """Extract transaction hash from deployment output."""
        import re
        # Look for transaction hash in various formats
        patterns = [
            r"Transaction ID: ([a-f0-9]+)",
            r"Transaction hash: ([a-f0-9]+)",
            r"([a-f0-9]{64})",  # 64-character hex string
        ]

        for pattern in patterns:
            match = re.search(pattern, output)
            if match:
                return match.group(1)

        return None

    def _parse_deployment_error(self, stderr: str) -> Dict[str, str]:
        """Parse deployment error message and code."""
        stderr = stderr.strip()

        if "configuration error" in stderr.lower():
            return {
                "code": "CONFIG_ERROR",
                "message": "Invalid flow.json configuration"
            }
        elif "account not found" in stderr.lower():
            return {
                "code": "ACCOUNT_NOT_FOUND",
                "message": "Flow account not found or not configured"
            }
        elif "invalid contract" in stderr.lower():
            return {
                "code": "INVALID_CONTRACT",
                "message": "Contract code is invalid or has syntax errors"
            }
        elif "insufficient funds" in stderr.lower():
            return {
                "code": "INSUFFICIENT_FUNDS",
                "message": "Insufficient funds in deployment account"
            }
        else:
            return {
                "code": "UNKNOWN_ERROR",
                "message": stderr[:500]  # Limit error message length
            }

    async def create_transaction_proposal(
        self,
        generated_config: GeneratedConfiguration,
        transaction_type: TransactionType,
        transaction_data: Dict[str, Any]
    ) -> TransactionProposal:
        """Create a transaction proposal for user approval."""
        try:
            # Estimate gas cost
            estimated_gas = await self._estimate_gas_cost(
                generated_config,
                transaction_type,
                transaction_data
            )

            proposal = TransactionProposal(
                config_id=generated_config.id,
                transaction_type=transaction_type,
                transaction_data=transaction_data,
                estimated_gas=estimated_gas,
                user_approval_status=ApprovalStatus.PENDING
            )

            self.db_session.add(proposal)
            self.db_session.commit()

            logger.info(f"Created transaction proposal for config {generated_config.id}")

            return proposal

        except Exception as e:
            logger.error(f"Failed to create transaction proposal for config {generated_config.id}: {e}")
            raise RuntimeError(f"Transaction proposal creation failed: {e}")

    async def _estimate_gas_cost(
        self,
        generated_config: GeneratedConfiguration,
        transaction_type: TransactionType,
        transaction_data: Dict[str, Any]
    ) -> int:
        """Estimate gas cost for a transaction."""
        # For now, use base estimates based on transaction type
        # In a production system, this would use Flow CLI to get actual estimates

        base_estimates = {
            TransactionType.DEPLOY: 100,
            TransactionType.UPDATE: 50,
            TransactionType.INTERACT: 20
        }

        base_cost = base_estimates.get(transaction_type, 50)

        # Add complexity multiplier based on transaction data size
        data_size = len(json.dumps(transaction_data))
        complexity_multiplier = max(1, data_size // 1000)  # 1KB chunks

        return base_cost * complexity_multiplier

    async def execute_approved_transaction(
        self,
        proposal: TransactionProposal,
        network: FlowNetwork = FlowNetwork.TESTNET
    ) -> Dict[str, Any]:
        """Execute an approved transaction."""
        if proposal.user_approval_status != ApprovalStatus.APPROVED:
            raise ValueError("Transaction must be approved before execution")

        try:
            # Create transaction file
            project_path = self.create_project_structure(f"tx_{proposal.id}")
            transaction_file = self._create_transaction_file(
                project_path,
                proposal.transaction_type,
                proposal.transaction_data
            )

            # Execute transaction
            execution_result = await self._execute_transaction(
                project_path,
                transaction_file,
                network
            )

            # Update proposal status
            proposal.responded_at = datetime.utcnow()
            if execution_result["success"]:
                proposal.signed_transaction = execution_result.get("transaction_hash")

            self.db_session.commit()

            return execution_result

        except Exception as e:
            logger.error(f"Transaction execution failed for proposal {proposal.id}: {e}")
            raise RuntimeError(f"Transaction execution failed: {e}")

    def _create_transaction_file(
        self,
        project_path: Path,
        transaction_type: TransactionType,
        transaction_data: Dict[str, Any]
    ) -> str:
        """Create a transaction file for execution."""
        transaction_template = self._get_transaction_template(transaction_type)

        # Fill in transaction data
        transaction_content = transaction_template.format(**transaction_data)

        transaction_file = project_path / "transactions" / f"tx_{transaction_type.value.lower()}.cdc"
        with open(transaction_file, 'w') as f:
            f.write(transaction_content)

        return str(transaction_file)

    def _get_transaction_template(self, transaction_type: TransactionType) -> str:
        """Get transaction template for a transaction type."""
        templates = {
            TransactionType.DEPLOY: """
                import FungibleToken from 0xFT
                import NonFungibleToken from 0xNFT

                transaction {{
                    prepare(signer: AuthAccount) {{
                        // Deployment logic here
                        log("Contract deployed")
                    }}
                }}
            """,
            TransactionType.UPDATE: """
                import SmartContract from 0xCONTRACT

                transaction {{
                    prepare(signer: AuthAccount) {{
                        // Update logic here
                        log("Contract updated")
                    }}
                }}
            """,
            TransactionType.INTERACT: """
                import SmartContract from 0xCONTRACT

                transaction(arg1: String, arg2: Int) {{
                    prepare(signer: AuthAccount) {{
                        // Interaction logic here
                        log("Contract interaction executed")
                    }}
                    execute {{
                        // Execute logic here
                    }}
                }}
            """
        }

        return templates.get(transaction_type, templates[TransactionType.INTERACT])

    async def _execute_transaction(
        self,
        project_path: Path,
        transaction_file: str,
        network: FlowNetwork
    ) -> Dict[str, Any]:
        """Execute a transaction using Flow CLI."""
        try:
            os.chdir(project_path)

            cmd = [
                "flow", "transactions", "send",
                transaction_file,
                "--network", network.value,
                "--signer", "default"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            if result.returncode == 0:
                transaction_hash = self._extract_transaction_hash(result.stdout)
                return {
                    "success": True,
                    "transaction_hash": transaction_hash,
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "output": result.stdout
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Transaction timed out after 2 minutes"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def validate_project_configuration(self, config: Dict[str, Any]) -> bool:
        """Validate a flow.json configuration."""
        required_keys = ["contracts", "networks", "accounts"]
        return all(key in config for key in required_keys)