"""
Smart Contract LLM Builder Python SDK

A comprehensive Python client for interacting with the Smart Contract LLM Builder API.
"""

import os
import json
import time
import requests
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base exception for API errors."""
    def __init__(self, message: str, code: str = None, details: Dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(APIError):
    """Authentication related errors."""
    pass


class NetworkError(APIError):
    """Network related errors."""
    pass


class ValidationError(APIError):
    """Validation related errors."""
    pass


class DeploymentError(APIError):
    """Deployment related errors."""
    pass


class FlowNetwork(Enum):
    """Flow blockchain networks."""
    TESTNET = "testnet"
    MAINNET = "mainnet"


class InputType(Enum):
    """Contract input types."""
    NATURAL_LANGUAGE = "NATURAL_LANGUAGE"
    CDC_FILE = "CDC_FILE"
    SOL_FILE = "SOL_FILE"


class DeploymentStatus(Enum):
    """Deployment status."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


@dataclass
class ContractSubmission:
    """Contract submission data model."""
    id: str
    user_id: str
    input_type: InputType
    content: str
    status: str
    pre_conditions: Optional[Dict] = None
    post_conditions: Optional[Dict] = None
    generated_config: Optional[Dict] = None
    deployments: Optional[List[Dict]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class DeploymentLog:
    """Deployment log data model."""
    id: str
    submission_id: str
    config_id: str
    network: str
    status: DeploymentStatus
    transaction_hash: Optional[str] = None
    contract_address: Optional[str] = None
    gas_used: Optional[int] = None
    execution_time_ms: Optional[int] = None
    log_content: Optional[str] = None
    error_details: Optional[Dict] = None
    created_at: Optional[datetime] = None


@dataclass
class UserInfo:
    """User information data model."""
    id: str
    email: str
    persona_type: str
    full_name: Optional[str] = None
    organization: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None


class SmartContractClient:
    """Main client class for Smart Contract LLM Builder API."""

    def __init__(
        self,
        base_url: str = None,
        email: str = None,
        password: str = None,
        token: str = None,
        timeout: int = 30,
        retry_attempts: int = 3
    ):
        """
        Initialize the Smart Contract client.

        Args:
            base_url: API base URL (defaults to environment variable)
            email: User email (for authentication)
            password: User password (for authentication)
            token: JWT token (alternative to email/password)
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts for failed requests
        """
        self.base_url = base_url or os.getenv('SMART_CONTRACT_API_URL', 'http://localhost:8000/api/v1')
        self.email = email or os.getenv('SMART_CONTRACT_EMAIL')
        self.password = password or os.getenv('SMART_CONTRACT_PASSWORD')
        self.token = token or os.getenv('SMART_CONTRACT_TOKEN')
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.session = requests.Session()

        # Set up session headers
        if self.token:
            self.session.headers.update({'Authorization': f'Bearer {self.token}'})

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Dict = None,
        files: Dict = None,
        params: Dict = None,
        retry_count: int = 0
    ) -> Dict:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body data
            files: Files to upload
            params: Query parameters
            retry_count: Current retry attempt count

        Returns:
            Response data as dictionary

        Raises:
            APIError: For API-related errors
            NetworkError: For network-related errors
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                files=files,
                params=params,
                timeout=self.timeout
            )

            # Handle HTTP errors
            if response.status_code == 401:
                raise AuthenticationError("Authentication required")
            elif response.status_code == 403:
                raise AuthenticationError("Insufficient permissions")
            elif response.status_code == 404:
                raise APIError("Resource not found", "NOT_FOUND")
            elif response.status_code == 422:
                raise ValidationError("Request validation failed")
            elif response.status_code == 429:
                raise APIError("Rate limit exceeded", "RATE_LIMIT_EXCEEDED")
            elif response.status_code >= 500:
                raise NetworkError(f"Server error: {response.status_code}")
            elif not response.ok:
                raise APIError(f"HTTP error: {response.status_code}")

            # Parse response
            response_data = response.json()

            # Check for API errors
            if not response_data.get('success', True):
                error_info = response_data.get('error', {})
                raise APIError(
                    message=error_info.get('message', 'Unknown API error'),
                    code=error_info.get('code'),
                    details=error_info.get('details')
                )

            return response_data

        except requests.exceptions.Timeout:
            if retry_count < self.retry_attempts:
                logger.warning(f"Request timeout, retrying ({retry_count + 1}/{self.retry_attempts})")
                time.sleep(2 ** retry_count)  # Exponential backoff
                return self._make_request(method, endpoint, data, files, params, retry_count + 1)
            raise NetworkError("Request timeout")

        except requests.exceptions.ConnectionError:
            if retry_count < self.retry_attempts:
                logger.warning(f"Connection error, retrying ({retry_count + 1}/{self.retry_attempts})")
                time.sleep(2 ** retry_count)
                return self._make_request(method, endpoint, data, files, params, retry_count + 1)
            raise NetworkError("Connection error")

        except json.JSONDecodeError:
            raise APIError("Invalid JSON response")

    def login(self, email: str = None, password: str = None) -> Dict:
        """
        Authenticate user and get JWT token.

        Args:
            email: User email (overrides constructor value)
            password: User password (overrides constructor value)

        Returns:
            Authentication response with token and user info

        Raises:
            AuthenticationError: If authentication fails
        """
        email = email or self.email
        password = password or self.password

        if not email or not password:
            raise AuthenticationError("Email and password required")

        data = {'email': email, 'password': password}
        response = self._make_request('POST', '/users/login', data=data)

        # Update token and session headers
        self.token = response['data']['access_token']
        self.session.headers.update({'Authorization': f'Bearer {self.token}'})

        logger.info(f"Successfully logged in as {email}")
        return response

    def get_user_info(self) -> UserInfo:
        """
        Get current user information.

        Returns:
            UserInfo object with user details
        """
        response = self._make_request('GET', '/users/me')
        user_data = response['data']

        return UserInfo(
            id=user_data['id'],
            email=user_data['email'],
            persona_type=user_data['persona_type'],
            full_name=user_data.get('full_name'),
            organization=user_data.get('organization'),
            is_active=user_data['is_active'],
            created_at=datetime.fromisoformat(user_data['created_at']) if user_data.get('created_at') else None
        )

    def update_user_profile(self, updates: Dict) -> UserInfo:
        """
        Update user profile.

        Args:
            updates: Dictionary of profile updates

        Returns:
            Updated UserInfo object
        """
        response = self._make_request('PUT', '/users/me', data=updates)
        user_data = response['data']

        return UserInfo(
            id=user_data['id'],
            email=user_data['email'],
            persona_type=user_data['persona_type'],
            full_name=user_data.get('full_name'),
            organization=user_data.get('organization'),
            is_active=user_data['is_active'],
            created_at=datetime.fromisoformat(user_data['created_at']) if user_data.get('created_at') else None
        )

    def generate_contract(
        self,
        description: str,
        network: FlowNetwork = FlowNetwork.TESTNET,
        pre_conditions: Optional[Dict] = None,
        post_conditions: Optional[Dict] = None
    ) -> ContractSubmission:
        """
        Generate a smart contract from natural language description.

        Args:
            description: Natural language description of the contract
            network: Target blockchain network
            pre_conditions: Pre-conditions for contract generation
            post_conditions: Expected post-conditions

        Returns:
            ContractSubmission object with generated contract
        """
        data = {
            'input_type': InputType.NATURAL_LANGUAGE.value,
            'content': description,
            'network': network.value
        }

        if pre_conditions:
            data['pre_conditions'] = pre_conditions
        if post_conditions:
            data['post_conditions'] = post_conditions

        response = self._make_request('POST', '/contracts', data=data)
        submission_data = response['data']

        return ContractSubmission(
            id=submission_data['submission_id'],
            user_id=submission_data['user_id'],
            input_type=InputType(submission_data['input_type']),
            content=submission_data['content'],
            status=submission_data['status'],
            pre_conditions=submission_data.get('pre_conditions'),
            post_conditions=submission_data.get('post_conditions'),
            generated_config=submission_data.get('generated_config'),
            deployments=submission_data.get('deployments'),
            created_at=datetime.fromisoformat(submission_data['created_at']) if submission_data.get('created_at') else None,
            updated_at=datetime.fromisoformat(submission_data['updated_at']) if submission_data.get('updated_at') else None
        )

    def upload_contract_file(
        self,
        file_path: str,
        network: FlowNetwork = FlowNetwork.TESTNET
    ) -> ContractSubmission:
        """
        Upload a contract file for processing.

        Args:
            file_path: Path to contract file (.cdc or .sol)
            network: Target blockchain network

        Returns:
            ContractSubmission object with processed contract
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
            data = {'network': network.value}

            response = self._make_request('POST', '/contracts/file', data=data, files=files)
            submission_data = response['data']

            return ContractSubmission(
                id=submission_data['submission_id'],
                user_id=submission_data['user_id'],
                input_type=InputType(submission_data['input_type']),
                content=submission_data['content'],
                status=submission_data['status'],
                generated_config=submission_data.get('generated_config'),
                created_at=datetime.fromisoformat(submission_data['created_at']) if submission_data.get('created_at') else None,
                updated_at=datetime.fromisoformat(submission_data['updated_at']) if submission_data.get('updated_at') else None
            )

    def get_contract_submission(self, submission_id: str) -> ContractSubmission:
        """
        Get details of a contract submission.

        Args:
            submission_id: Contract submission ID

        Returns:
            ContractSubmission object
        """
        response = self._make_request('GET', f'/contracts/{submission_id}')
        submission_data = response['data']

        return ContractSubmission(
            id=submission_data['id'],
            user_id=submission_data['user_id'],
            input_type=InputType(submission_data['input_type']),
            content=submission_data['content'],
            status=submission_data['status'],
            pre_conditions=submission_data.get('pre_conditions'),
            post_conditions=submission_data.get('post_conditions'),
            generated_config=submission_data.get('generated_config'),
            deployments=submission_data.get('deployments'),
            created_at=datetime.fromisoformat(submission_data['created_at']) if submission_data.get('created_at') else None,
            updated_at=datetime.fromisoformat(submission_data['updated_at']) if submission_data.get('updated_at') else None
        )

    def list_contract_submissions(
        self,
        limit: int = 10,
        offset: int = 0,
        status: Optional[str] = None,
        input_type: Optional[InputType] = None
    ) -> Dict:
        """
        List user's contract submissions.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            status: Filter by status
            input_type: Filter by input type

        Returns:
            Dictionary with submissions list and pagination info
        """
        params = {'limit': limit, 'offset': offset}
        if status:
            params['status'] = status
        if input_type:
            params['input_type'] = input_type.value

        return self._make_request('GET', '/contracts', params=params)

    def deploy_contract(
        self,
        submission_id: str,
        network: FlowNetwork = FlowNetwork.TESTNET,
        config_id: Optional[str] = None,
        gas_limit: Optional[int] = None
    ) -> DeploymentLog:
        """
        Deploy a contract to the blockchain.

        Args:
            submission_id: Contract submission ID
            network: Target blockchain network
            config_id: Configuration ID (if multiple configs exist)
            gas_limit: Gas limit for deployment

        Returns:
            DeploymentLog object with deployment details
        """
        data = {'network': network.value}
        if config_id:
            data['config_id'] = config_id
        if gas_limit:
            data['gas_limit'] = gas_limit

        response = self._make_request('POST', f'/contracts/{submission_id}/deploy', data=data)
        deployment_data = response['data']

        return DeploymentLog(
            id=deployment_data['deployment_id'],
            submission_id=deployment_data['submission_id'],
            config_id=deployment_data['config_id'],
            network=deployment_data['network'],
            status=DeploymentStatus(deployment_data['status']),
            transaction_hash=deployment_data.get('transaction_hash'),
            contract_address=deployment_data.get('contract_address'),
            gas_used=deployment_data.get('gas_used'),
            execution_time_ms=deployment_data.get('execution_time_ms'),
            log_content=deployment_data.get('log_content'),
            error_details=deployment_data.get('error_details'),
            created_at=datetime.fromisoformat(deployment_data['created_at']) if deployment_data.get('created_at') else None
        )

    def get_deployment_logs(self, submission_id: str) -> List[DeploymentLog]:
        """
        Get deployment history for a contract submission.

        Args:
            submission_id: Contract submission ID

        Returns:
            List of DeploymentLog objects
        """
        response = self._make_request('GET', f'/contracts/{submission_id}/deployments')
        deployments_data = response['data']['deployments']

        return [
            DeploymentLog(
                id=dep['id'],
                submission_id=dep['submission_id'],
                config_id=dep['config_id'],
                network=dep['network'],
                status=DeploymentStatus(dep['status']),
                transaction_hash=dep.get('transaction_hash'),
                contract_address=dep.get('contract_address'),
                gas_used=dep.get('gas_used'),
                execution_time_ms=dep.get('execution_time_ms'),
                log_content=dep.get('log_content'),
                error_details=dep.get('error_details'),
                created_at=datetime.fromisoformat(dep['created_at']) if dep.get('created_at') else None
            )
            for dep in deployments_data
        ]

    def search_documentation(
        self,
        query: str,
        limit: int = 10,
        use_semantic_search: bool = True,
        content_types: Optional[List[str]] = None,
        sources: Optional[List[str]] = None
    ) -> Dict:
        """
        Search documentation.

        Args:
            query: Search query
            limit: Maximum number of results
            use_semantic_search: Enable semantic search
            content_types: Filter by content types
            sources: Filter by sources

        Returns:
            Search results dictionary
        """
        data = {
            'query': query,
            'limit': limit,
            'use_semantic_search': use_semantic_search
        }

        if content_types:
            data['content_types'] = content_types
        if sources:
            data['sources'] = sources

        return self._make_request('POST', '/documentation/search', data=data)

    def get_learning_insights(self, limit: int = 10, pattern_type: Optional[str] = None) -> Dict:
        """
        Get learning insights and patterns.

        Args:
            limit: Maximum number of insights
            pattern_type: Filter by pattern type

        Returns:
            Learning insights dictionary
        """
        params = {'limit': limit}
        if pattern_type:
            params['pattern_type'] = pattern_type

        return self._make_request('GET', '/learning/insights', params=params)

    def get_statistics(self) -> Dict:
        """
        Get system statistics.

        Returns:
            System statistics dictionary
        """
        return self._make_request('GET', '/statistics')

    def export_user_data(self, format: str = 'JSON', include: Optional[List[str]] = None) -> Dict:
        """
        Export user data.

        Args:
            format: Export format (JSON, CSV)
            include: Data types to include

        Returns:
            Export information dictionary
        """
        data = {'format': format}
        if include:
            data['include'] = include

        return self._make_request('POST', '/users/me/export-data', data=data)

    def wait_for_deployment(
        self,
        deployment_id: str,
        timeout: int = 300,
        poll_interval: int = 5
    ) -> DeploymentLog:
        """
        Wait for deployment to complete.

        Args:
            deployment_id: Deployment ID to monitor
            timeout: Maximum wait time in seconds
            poll_interval: Polling interval in seconds

        Returns:
            Final DeploymentLog object

        Raises:
            DeploymentError: If deployment fails or times out
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Note: This would require a get_deployment_by_id endpoint
            # For now, we'll simulate the behavior
            time.sleep(poll_interval)

            # In a real implementation, you would:
            # 1. Call get_deployment_by_id(deployment_id)
            # 2. Check if status is terminal (SUCCESS, FAILED, TIMEOUT)
            # 3. Return if complete, continue if still processing

        raise DeploymentError("Deployment timeout")

    def validate_generated_contract(self, submission_id: str) -> Dict:
        """
        Validate a generated contract.

        Args:
            submission_id: Contract submission ID

        Returns:
            Validation results dictionary
        """
        return self._make_request('POST', f'/contracts/{submission_id}/validate')

    def optimize_contract(self, submission_id: str, optimization_level: str = 'standard') -> Dict:
        """
        Optimize a generated contract.

        Args:
            submission_id: Contract submission ID
            optimization_level: Optimization level (basic, standard, aggressive)

        Returns:
            Optimization results dictionary
        """
        data = {'optimization_level': optimization_level}
        return self._make_request('POST', f'/contracts/{submission_id}/optimize', data=data)