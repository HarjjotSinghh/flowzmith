import subprocess
import json
from typing import Dict, Any, Optional
from src.config import settings

class FlowService:
    def __init__(self):
        self.network = settings.FLOW_NETWORK
        self.account_address = settings.FLOW_ACCOUNT_ADDRESS

    async def deploy_contract(
        self,
        contract_code: str,
        contract_name: str,
        network: Optional[str] = None
    ) -> Dict[str, Any]:
        """Deploy contract to Flow blockchain"""
        network = network or self.network

        try:
            # Write contract to temporary file
            contract_file = f"/tmp/{contract_name}.cdc"
            with open(contract_file, "w") as f:
                f.write(contract_code)

            # Deploy contract using Flow CLI
            result = subprocess.run([
                "flow", "project", "deploy",
                "--network", network,
                "--update", "true"
            ], capture_output=True, text=True, check=True)

            # Parse deployment result
            deployment_info = self._parse_deployment_result(result.stdout)

            return {
                "success": True,
                "transaction_hash": deployment_info.get("transaction_hash"),
                "contract_address": deployment_info.get("contract_address"),
                "gas_used": deployment_info.get("gas_used", 0)
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error_message": e.stderr,
                "exit_code": e.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "error_message": str(e)
            }

    def _parse_deployment_result(self, output: str) -> Dict[str, Any]:
        """Parse Flow CLI deployment output"""
        # This is a simplified parser - in practice, you'd want more robust parsing
        lines = output.split('\n')
        result = {}

        for line in lines:
            if 'Transaction ID:' in line:
                result['transaction_hash'] = line.split('Transaction ID:')[1].strip()
            elif 'Contract Address:' in line:
                result['contract_address'] = line.split('Contract Address:')[1].strip()
            elif 'Gas Used:' in line:
                result['gas_used'] = int(line.split('Gas Used:')[1].strip())

        return result

    async def get_account_info(self, address: str) -> Dict[str, Any]:
        """Get account information from Flow blockchain"""
        try:
            result = subprocess.run([
                "flow", "accounts", "get", address
            ], capture_output=True, text=True, check=True)

            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            return {"error": e.stderr}
        except Exception as e:
            return {"error": str(e)}

    async def estimate_gas(self, contract_code: str) -> int:
        """Estimate gas for contract deployment"""
        # This is a simplified implementation
        # In practice, you'd use Flow's gas estimation API
        base_gas = 100000  # Base deployment cost
        code_size = len(contract_code)
        estimated_gas = base_gas + (code_size // 100) * 1000

        return estimated_gas