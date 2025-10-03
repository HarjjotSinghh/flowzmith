"""
Auto-generated Python schema from TypeScript definitions.
DO NOT EDIT MANUALLY - regenerate using: npm run generate-python
"""

from typing import TypedDict, Literal, Optional, List, Dict, Any
from enum import Enum

# ============================================================================
# CLI Command Types
# ============================================================================

class CLICommandType(str, Enum):
    SETUP = "setup"
    CREATE_CONTRACT = "create_contract"
    DEPLOY_CONTRACT = "deploy_contract"
    SEARCH_DOCS = "search_docs"
    UPLOAD_DOCS = "upload_docs"
    BROWSE_DOCS = "browse_docs"
    CRAWL_DOCS = "crawl_docs"
    FIRECRAWL_SEARCH = "firecrawl_search"
    LIST_DEPLOYMENTS = "list_deployments"
    STATUS = "status"
    WIZARD = "wizard"
    GENERATE_FROM_CONTEXT = "generate_from_context"
    MCP_EXPLORER = "mcp_explorer"
    FLOW_INIT = "flow_init"
    FLOW_DEPLOY = "flow_deploy"
    FLOW_STATUS = "flow_status"
    FLOW_LIST = "flow_list"
    FLOW_GENERATE_DEPLOY = "flow_generate_deploy"
    FLOW_AUTO = "flow_auto"
    CHAT = "chat"

NetworkType = Literal["emulator", "testnet", "mainnet"]
StatusType = Literal["success", "failed", "pending", "deployed", "queued"]

# ============================================================================
# Request Types
# ============================================================================

class CreateContractRequest(TypedDict, total=False):
    requirements: str
    context: Optional[str]
    pre_conditions: Optional[Dict[str, Any]]
    post_conditions: Optional[Dict[str, Any]]
    network: NetworkType
    input_method: Optional[str]

class DeployContractRequest(TypedDict, total=False):
    contract_id: Optional[str]
    contract_name: str
    contract_content: str
    network: NetworkType
    auto_deploy: bool
    account_config: Optional[Dict[str, str]]

class SearchDocsRequest(TypedDict):
    query: str
    limit: int

class FlowInitRequest(TypedDict, total=False):
    name: Optional[str]
    directory: Optional[str]

class GenerateFromContextRequest(TypedDict, total=False):
    requirements: str
    context_dir: Optional[str]
    network: NetworkType
    stream: bool
    auto_deploy: bool
    flow_init: bool

# ============================================================================
# Response Types
# ============================================================================

class CreateContractResponse(TypedDict, total=False):
    status: StatusType
    submission_id: Optional[str]
    generated_contract_code: Optional[str]
    config_content: Optional[Any]
    contract_name: Optional[str]
    validation_status: Optional[str]
    error: Optional[str]
    project_dir: Optional[str]

class DeployContractResponse(TypedDict, total=False):
    status: StatusType
    deployment_id: Optional[str]
    project_id: Optional[str]
    project_dir: Optional[str]
    transaction_id: Optional[str]
    deployment_output: Optional[str]
    error: Optional[str]

class DocumentResult(TypedDict, total=False):
    id: str
    title: str
    content: str
    category: Optional[str]
    relevance_score: Optional[float]

class SearchDocsResponse(TypedDict):
    results: List[DocumentResult]
    total: int

class FlowInitResponse(TypedDict, total=False):
    status: StatusType
    project_dir: Optional[str]
    project_id: Optional[str]
    error: Optional[str]

class SystemStatusResponse(TypedDict):
    server_status: Literal["healthy", "unhealthy"]
    database_status: Literal["connected", "disconnected"]
    total_contracts: int
    successful_deployments: int
    pending_submissions: int
    total_docs: int
