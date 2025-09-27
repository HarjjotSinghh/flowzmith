"""
Deployment Service for Flowzmith.

Handles automatic deployment of generated contracts using Flow CLI,
including project initialization, contract setup, and deployment automation.
"""

import asyncio
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from .flow_manager import FlowProjectManager

logger = logging.getLogger(__name__)

class ContractDeploymentService:
    """Service for automating contract deployment workflow."""
    
    def __init__(self, flow_manager: FlowProjectManager = None):
        """Initialize deployment service.
        
        Args:
            flow_manager: Flow project manager instance. Creates new if None.
        """
        self.flow_manager = flow_manager or FlowProjectManager()
        self.deployment_queue = asyncio.Queue()
        self.deployment_history: List[Dict[str, Any]] = []
        self._deployment_task = None
        logger.info("ContractDeploymentService initialized")
    
    async def start_deployment_worker(self):
        """Start the background deployment worker."""
        if self._deployment_task is None or self._deployment_task.done():
            self._deployment_task = asyncio.create_task(self._deployment_worker())
            logger.info("Deployment worker started")
    
    async def stop_deployment_worker(self):
        """Stop the background deployment worker."""
        if self._deployment_task and not self._deployment_task.done():
            self._deployment_task.cancel()
            try:
                await self._deployment_task
            except asyncio.CancelledError:
                pass
            logger.info("Deployment worker stopped")
    
    async def deploy_contract_automatically(self, contract_name: str, contract_content: str,
                                          network: str = "emulator", 
                                          auto_deploy: bool = True) -> Dict[str, Any]:
        """Automatically deploy a contract with Flow CLI.
        
        Args:
            contract_name: Name of the contract
            contract_content: Cadence contract source code
            network: Target network (emulator, testnet, mainnet)
            auto_deploy: Whether to automatically deploy after project creation
            
        Returns:
            Dict containing deployment result and project information
        """
        deployment_id = str(uuid.uuid4())
        project_id = f"contract_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{deployment_id[:8]}"
        
        logger.info("Starting automatic deployment: contract=%s, project_id=%s, network=%s", 
                   contract_name, project_id, network)
        
        deployment_record = {
            "deployment_id": deployment_id,
            "project_id": project_id,
            "contract_name": contract_name,
            "network": network,
            "auto_deploy": auto_deploy,
            "started_at": datetime.now().isoformat(),
            "status": "initializing"
        }
        
        try:
            # Check if Flow CLI is available
            if not await self.flow_manager.check_flow_cli_installed():
                raise Exception("Flow CLI is not installed or not accessible")
            
            # Create Flow project
            deployment_record["status"] = "creating_project"
            project_result = await self.flow_manager.create_flow_project(
                project_id=project_id,
                contract_name=contract_name,
                contract_content=contract_content,
                network=network
            )
            
            if project_result.get("status") != "success":
                raise Exception(f"Project creation failed: {project_result.get('error', 'Unknown error')}")
            
            deployment_record.update({
                "project_created_at": datetime.now().isoformat(),
                "project_dir": project_result.get("project_dir"),
                "project_metadata": project_result.get("metadata")
            })
            
            # Deploy contract if auto_deploy is enabled
            if auto_deploy:
                deployment_record["status"] = "deploying"
                deploy_result = await self.flow_manager.deploy_contract(
                    project_id=project_id,
                    network=network
                )
                
                if deploy_result.get("status") == "success":
                    deployment_record.update({
                        "status": "deployed",
                        "deployed_at": deploy_result.get("deployed_at"),
                        "deployment_output": deploy_result.get("deployment_output"),
                        "deployment_network": network
                    })
                    logger.info("Contract deployed successfully: %s", project_id)
                else:
                    deployment_record.update({
                        "status": "deployment_failed",
                        "deployment_error": deploy_result.get("error")
                    })
                    logger.error("Deployment failed for %s: %s", project_id, deploy_result.get("error"))
            else:
                deployment_record["status"] = "project_ready"
                logger.info("Project created, deployment skipped: %s", project_id)
            
            deployment_record["completed_at"] = datetime.now().isoformat()
            
        except Exception as e:
            logger.exception("Deployment failed for %s", project_id)
            deployment_record.update({
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            })
        
        # Add to deployment history
        self.deployment_history.append(deployment_record)
        
        # Keep only last 100 deployments in memory
        if len(self.deployment_history) > 100:
            self.deployment_history = self.deployment_history[-100:]
        
        return deployment_record
    
    async def queue_deployment(self, contract_name: str, contract_content: str,
                             network: str = "emulator", auto_deploy: bool = True) -> str:
        """Queue a contract for deployment.
        
        Args:
            contract_name: Name of the contract
            contract_content: Cadence contract source code
            network: Target network
            auto_deploy: Whether to automatically deploy
            
        Returns:
            Deployment ID for tracking
        """
        deployment_id = str(uuid.uuid4())
        
        deployment_request = {
            "deployment_id": deployment_id,
            "contract_name": contract_name,
            "contract_content": contract_content,
            "network": network,
            "auto_deploy": auto_deploy,
            "queued_at": datetime.now().isoformat()
        }
        
        await self.deployment_queue.put(deployment_request)
        logger.info("Deployment queued: %s for contract %s", deployment_id, contract_name)
        
        return deployment_id
    
    async def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a deployment by ID.
        
        Args:
            deployment_id: Deployment identifier
            
        Returns:
            Deployment record or None if not found
        """
        for record in self.deployment_history:
            if record.get("deployment_id") == deployment_id:
                return record
        return None
    
    async def get_recent_deployments(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent deployment records.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of recent deployment records
        """
        return self.deployment_history[-limit:] if self.deployment_history else []
    
    async def get_project_deployments(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all deployments for a specific project.
        
        Args:
            project_id: Project identifier
            
        Returns:
            List of deployment records for the project
        """
        return [
            record for record in self.deployment_history
            if record.get("project_id") == project_id
        ]
    
    async def redeploy_contract(self, project_id: str, network: str = None) -> Dict[str, Any]:
        """Redeploy an existing contract project.
        
        Args:
            project_id: Project identifier
            network: Target network (uses original if None)
            
        Returns:
            Deployment result
        """
        logger.info("Redeploying contract: project_id=%s, network=%s", project_id, network)
        
        # Get project status
        project_status = await self.flow_manager.get_project_status(project_id)
        if project_status.get("status") != "found":
            return {
                "status": "failed",
                "error": f"Project {project_id} not found"
            }
        
        # Use original network if not specified
        if network is None:
            metadata = project_status.get("metadata", {})
            network = metadata.get("network", "emulator")
        
        # Deploy the contract
        deploy_result = await self.flow_manager.deploy_contract(project_id, network)
        
        # Create deployment record
        deployment_record = {
            "deployment_id": str(uuid.uuid4()),
            "project_id": project_id,
            "contract_name": project_status.get("metadata", {}).get("contract_name", "Unknown"),
            "network": network,
            "type": "redeploy",
            "started_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            **deploy_result
        }
        
        self.deployment_history.append(deployment_record)
        
        return deployment_record
    
    async def _deployment_worker(self):
        """Background worker that processes deployment queue."""
        logger.info("Deployment worker started")
        
        try:
            while True:
                # Wait for deployment request
                deployment_request = await self.deployment_queue.get()
                
                try:
                    logger.info("Processing deployment: %s", deployment_request.get("deployment_id"))
                    
                    # Execute deployment
                    result = await self.deploy_contract_automatically(
                        contract_name=deployment_request["contract_name"],
                        contract_content=deployment_request["contract_content"],
                        network=deployment_request["network"],
                        auto_deploy=deployment_request["auto_deploy"]
                    )
                    
                    logger.info("Deployment completed: %s with status %s", 
                               deployment_request.get("deployment_id"), result.get("status"))
                    
                except Exception as e:
                    logger.exception("Deployment worker error for %s", 
                                   deployment_request.get("deployment_id"))
                
                finally:
                    # Mark task as done
                    self.deployment_queue.task_done()
                    
        except asyncio.CancelledError:
            logger.info("Deployment worker cancelled")
            raise
        except Exception as e:
            logger.exception("Deployment worker crashed: %s", e)
    
    async def get_deployment_statistics(self) -> Dict[str, Any]:
        """Get deployment statistics.
        
        Returns:
            Dict containing deployment statistics
        """
        if not self.deployment_history:
            return {
                "total_deployments": 0,
                "successful_deployments": 0,
                "failed_deployments": 0,
                "success_rate": 0.0,
                "networks": {},
                "recent_activity": []
            }
        
        total = len(self.deployment_history)
        successful = len([r for r in self.deployment_history if r.get("status") == "deployed"])
        failed = len([r for r in self.deployment_history if r.get("status") in ["failed", "deployment_failed"]])
        
        # Network statistics
        networks = {}
        for record in self.deployment_history:
            network = record.get("network", "unknown")
            if network not in networks:
                networks[network] = {"total": 0, "successful": 0, "failed": 0}
            
            networks[network]["total"] += 1
            if record.get("status") == "deployed":
                networks[network]["successful"] += 1
            elif record.get("status") in ["failed", "deployment_failed"]:
                networks[network]["failed"] += 1
        
        return {
            "total_deployments": total,
            "successful_deployments": successful,
            "failed_deployments": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0.0,
            "networks": networks,
            "recent_activity": self.deployment_history[-10:] if self.deployment_history else []
        }