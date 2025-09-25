"""
Validation utilities and middleware for Smart Contract LLM Builder.
"""

import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from fastapi import HTTPException, status, Request
from pydantic import ValidationError, BaseModel
from sqlalchemy.orm import Session
import re
import json

from ..models import (
    User,
    ContractSubmission,
    GeneratedConfiguration,
    DeploymentLog
)
from ..schemas import InputType, SubmissionStatus
from ..config import get_settings

logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of a validation operation."""

    def __init__(
        self,
        is_valid: bool,
        errors: List[str] = None,
        warnings: List[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.details = details or {}


class InputValidator:
    """Validates user inputs and requests."""

    @staticmethod
    def validate_email(email: str) -> ValidationResult:
        """Validate email address format."""
        errors = []
        warnings = []

        # Basic email regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            errors.append("Invalid email format")

        # Check length
        if len(email) > 254:
            errors.append("Email address too long")

        # Check for suspicious patterns
        suspicious_patterns = [
            r'test.*@',
            r'dummy.*@',
            r'fake.*@',
            r'admin.*@',
            r'info.*@'
        ]

        for pattern in suspicious_patterns:
            if re.match(pattern, email, re.IGNORECASE):
                warnings.append("Email address appears to be a test or temporary account")
                break

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    @staticmethod
    def validate_password(password: str) -> ValidationResult:
        """Validate password strength."""
        errors = []
        warnings = []

        # Length requirement
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")

        # Complexity requirements
        if not re.search(r'[A-Z]', password):
            warnings.append("Password should contain at least one uppercase letter")

        if not re.search(r'[a-z]', password):
            warnings.append("Password should contain at least one lowercase letter")

        if not re.search(r'\d', password):
            warnings.append("Password should contain at least one number")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            warnings.append("Password should contain at least one special character")

        # Common weak passwords
        weak_passwords = [
            'password', '123456', 'qwerty', 'abc123',
            'letmein', 'admin', 'welcome', 'password123'
        ]

        if password.lower() in weak_passwords:
            errors.append("Password is too common and insecure")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    @staticmethod
    def validate_contract_content(content: str, input_type: InputType) -> ValidationResult:
        """Validate contract content based on input type."""
        errors = []
        warnings = []

        # Basic content validation
        if not content or content.strip() == "":
            errors.append("Contract content cannot be empty")

        # Length validation
        if len(content) > 50000:  # 50KB limit
            errors.append("Contract content too large")

        # Input type specific validation
        if input_type == InputType.CDC_FILE:
            validation_result = InputValidator._validate_cadence_code(content)
            errors.extend(validation_result.errors)
            warnings.extend(validation_result.warnings)

        elif input_type == InputType.SOL_FILE:
            validation_result = InputValidator._validate_solidity_code(content)
            errors.extend(validation_result.errors)
            warnings.extend(validation_result.warnings)

        elif input_type == InputType.NATURAL_LANGUAGE:
            validation_result = InputValidator._validate_natural_language(content)
            errors.extend(validation_result.errors)
            warnings.extend(validation_result.warnings)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    @staticmethod
    def _validate_cadence_code(code: str) -> ValidationResult:
        """Validate Cadence smart contract code."""
        errors = []
        warnings = []

        # Basic Cadence syntax checks
        if not any(keyword in code for keyword in ['pub contract', 'contract']):
            warnings.append("No contract declaration found")

        if 'resource' not in code:
            warnings.append("No resource definition found")

        if 'init(' not in code:
            warnings.append("No initializer found")

        # Check for common Cadence patterns
        required_patterns = [
            r'pub\s+let\s+\w+',
            r'pub\s+resource\s+\w+',
            r'init\s*\(',
            r'prepare\s*\(',
            r'execute\s*\{'
        ]

        for pattern in required_patterns:
            if not re.search(pattern, code):
                warnings.append(f"Missing expected Cadence pattern: {pattern}")

        # Check for potential issues
        if 'copy()' in code:
            errors.append("Resources cannot be copied - use move/borrow semantics")

        if 'destroy()' not in code and 'resource' in code:
            warnings.append("Resources should have destroy() methods")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    @staticmethod
    def _validate_solidity_code(code: str) -> ValidationResult:
        """Validate Solidity smart contract code."""
        errors = []
        warnings = []

        # Basic Solidity syntax checks
        if not any(keyword in code for keyword in ['contract', 'library', 'interface']):
            warnings.append("No contract/library/interface declaration found")

        if 'constructor' not in code and 'function' not in code:
            warnings.append("No functions found")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    @staticmethod
    def _validate_natural_language(text: str) -> ValidationResult:
        """Validate natural language input."""
        errors = []
        warnings = []

        # Length validation
        if len(text) < 10:
            warnings.append("Input is very short - may not provide enough detail")

        if len(text) > 5000:
            warnings.append("Input is very long - consider breaking it down")

        # Check for meaningful content
        meaningful_keywords = [
            'contract', 'smart', 'blockchain', 'token', 'nft',
            'create', 'deploy', 'function', 'state', 'transfer'
        ]

        found_keywords = sum(1 for keyword in meaningful_keywords if keyword.lower() in text.lower())
        if found_keywords < 2:
            warnings.append("Input may not contain enough blockchain/smart contract context")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    @staticmethod
    def validate_pre_conditions(pre_conditions: Optional[Dict[str, Any]]) -> ValidationResult:
        """Validate pre-conditions."""
        errors = []
        warnings = []

        if pre_conditions is None:
            return ValidationResult(is_valid=True)

        if not isinstance(pre_conditions, dict):
            errors.append("Pre-conditions must be a dictionary")

        # Check for expected keys
        expected_keys = ['accounts', 'tokens', 'permissions', 'network']
        for key in pre_conditions.keys():
            if key not in expected_keys:
                warnings.append(f"Unknown pre-condition key: {key}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    @staticmethod
    def validate_post_conditions(post_conditions: Optional[Dict[str, Any]]) -> ValidationResult:
        """Validate post-conditions."""
        errors = []
        warnings = []

        if post_conditions is None:
            return ValidationResult(is_valid=True)

        if not isinstance(post_conditions, dict):
            errors.append("Post-conditions must be a dictionary")

        # Check for expected keys
        expected_keys = ['deployed_contracts', 'created_resources', 'emitted_events']
        for key in post_conditions.keys():
            if key not in expected_keys:
                warnings.append(f"Unknown post-condition key: {key}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


class ConfigurationValidator:
    """Validates flow.json configurations."""

    @staticmethod
    def validate_flow_config(config: Dict[str, Any]) -> ValidationResult:
        """Validate flow.json configuration."""
        errors = []
        warnings = []

        # Required sections
        required_sections = ['contracts', 'networks', 'accounts']
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing required section: {section}")

        # Validate contracts section
        if 'contracts' in config:
            contracts_validation = ConfigurationValidator._validate_contracts_section(config['contracts'])
            errors.extend(contracts_validation.errors)
            warnings.extend(contracts_validation.warnings)

        # Validate networks section
        if 'networks' in config:
            networks_validation = ConfigurationValidator._validate_networks_section(config['networks'])
            errors.extend(networks_validation.errors)
            warnings.extend(networks_validation.warnings)

        # Validate accounts section
        if 'accounts' in config:
            accounts_validation = ConfigurationValidator._validate_accounts_section(config['accounts'])
            errors.extend(accounts_validation.errors)
            warnings.extend(accounts_validation.warnings)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    @staticmethod
    def _validate_contracts_section(contracts: Dict[str, Any]) -> ValidationResult:
        """Validate contracts section."""
        errors = []
        warnings = []

        if not isinstance(contracts, dict):
            errors.append("Contracts section must be a dictionary")
            return ValidationResult(is_valid=False, errors=errors)

        for contract_name, contract_config in contracts.items():
            if not isinstance(contract_config, dict):
                errors.append(f"Contract '{contract_name}' must be a dictionary")
                continue

            if 'source' not in contract_config:
                warnings.append(f"Contract '{contract_name}' missing source file")

            if 'aliases' in contract_config and not isinstance(contract_config['aliases'], dict):
                errors.append(f"Contract '{contract_name}' aliases must be a dictionary")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    @staticmethod
    def _validate_networks_section(networks: Dict[str, Any]) -> ValidationResult:
        """Validate networks section."""
        errors = []
        warnings = []

        if not isinstance(networks, dict):
            errors.append("Networks section must be a dictionary")
            return ValidationResult(is_valid=False, errors=errors)

        valid_networks = ['emulator', 'testnet', 'mainnet']
        for network_name, network_config in networks.items():
            if network_name not in valid_networks:
                warnings.append(f"Unknown network: {network_name}")

            if not isinstance(network_config, dict):
                errors.append(f"Network '{network_name}' must be a dictionary")
                continue

            if 'host' not in network_config:
                warnings.append(f"Network '{network_name}' missing host")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    @staticmethod
    def _validate_accounts_section(accounts: Dict[str, Any]) -> ValidationResult:
        """Validate accounts section."""
        errors = []
        warnings = []

        if not isinstance(accounts, dict):
            errors.append("Accounts section must be a dictionary")
            return ValidationResult(is_valid=False, errors=errors)

        for account_name, account_config in accounts.items():
            if not isinstance(account_config, dict):
                errors.append(f"Account '{account_name}' must be a dictionary")
                continue

            if 'address' not in account_config:
                errors.append(f"Account '{account_name}' missing address")

            elif not isinstance(account_config['address'], str):
                errors.append(f"Account '{account_name}' address must be a string")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


class DeploymentValidator:
    """Validates deployment requests and configurations."""

    @staticmethod
    def validate_deployment_request(
        config_id: str,
        network: str,
        user_id: str,
        db: Session
    ) -> ValidationResult:
        """Validate deployment request."""
        errors = []
        warnings = []

        # Validate network
        valid_networks = ['emulator', 'testnet', 'mainnet']
        if network not in valid_networks:
            errors.append(f"Invalid network: {network}")

        # Validate configuration exists and belongs to user
        config = db.query(GeneratedConfiguration).filter(
            GeneratedConfiguration.id == config_id
        ).first()

        if not config:
            errors.append("Configuration not found")

        elif str(config.contract_submission.user_id) != user_id:
            errors.append("Configuration does not belong to user")

        # Check if configuration is valid
        if config and config.validation_status != 'VALID':
            warnings.append("Configuration validation status is not VALID")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    @staticmethod
    def validate_transaction_proposal(
        config_id: str,
        transaction_type: str,
        transaction_data: Dict[str, Any],
        user_id: str,
        db: Session
    ) -> ValidationResult:
        """Validate transaction proposal."""
        errors = []
        warnings = []

        # Validate transaction type
        valid_types = ['DEPLOY', 'UPDATE', 'INTERACT']
        if transaction_type not in valid_types:
            errors.append(f"Invalid transaction type: {transaction_type}")

        # Validate configuration exists and belongs to user
        config = db.query(GeneratedConfiguration).filter(
            GeneratedConfiguration.id == config_id
        ).first()

        if not config:
            errors.append("Configuration not found")

        elif str(config.contract_submission.user_id) != user_id:
            errors.append("Configuration does not belong to user")

        # Validate transaction data
        if not isinstance(transaction_data, dict):
            errors.append("Transaction data must be a dictionary")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


class PydanticValidator:
    """Utility for Pydantic model validation."""

    @staticmethod
    def validate_model(model: BaseModel, data: Dict[str, Any]) -> ValidationResult:
        """Validate data against a Pydantic model."""
        try:
            model(**data)
            return ValidationResult(is_valid=True)
        except ValidationError as e:
            errors = []
            for error in e.errors():
                field_path = " -> ".join(str(loc) for loc in error["loc"])
                errors.append(f"{field_path}: {error['msg']}")
            return ValidationResult(is_valid=False, errors=errors)

    @staticmethod
    def validate_json(json_str: str) -> ValidationResult:
        """Validate JSON string."""
        try:
            data = json.loads(json_str)
            return ValidationResult(
                is_valid=True,
                details={"parsed_data": data}
            )
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Invalid JSON: {str(e)}"]
            )


class DatabaseValidator:
    """Validates database entities and relationships."""

    @staticmethod
    def validate_user_exists(user_id: str, db: Session) -> ValidationResult:
        """Validate that a user exists."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return ValidationResult(
                is_valid=False,
                errors=["User not found"]
            )
        return ValidationResult(is_valid=True)

    @staticmethod
    def validate_submission_ownership(submission_id: str, user_id: str, db: Session) -> ValidationResult:
        """Validate that a submission belongs to a user."""
        submission = db.query(ContractSubmission).filter(
            ContractSubmission.id == submission_id
        ).first()

        if not submission:
            return ValidationResult(
                is_valid=False,
                errors=["Submission not found"]
            )

        if str(submission.user_id) != user_id:
            return ValidationResult(
                is_valid=False,
                errors=["Submission does not belong to user"]
            )

        return ValidationResult(is_valid=True)

    @staticmethod
    def validate_config_ownership(config_id: str, user_id: str, db: Session) -> ValidationResult:
        """Validate that a configuration belongs to a user."""
        config = db.query(GeneratedConfiguration).filter(
            GeneratedConfiguration.id == config_id
        ).first()

        if not config:
            return ValidationResult(
                is_valid=False,
                errors=["Configuration not found"]
            )

        if str(config.contract_submission.user_id) != user_id:
            return ValidationResult(
                is_valid=False,
                errors=["Configuration does not belong to user"]
            )

        return ValidationResult(is_valid=True)


# Validation middleware for FastAPI
class ValidationMiddleware:
    """Middleware for request validation."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        """Process validation for incoming requests."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Create request object
        from fastapi import Request
        request = Request(scope, receive)

        # Validate request
        validation_result = await self._validate_request(request)

        if not validation_result.is_valid:
            # Return validation error
            from fastapi.responses import JSONResponse
            response = JSONResponse(
                status_code=422,
                content={
                    "detail": "Validation failed",
                    "errors": validation_result.errors,
                    "warnings": validation_result.warnings
                }
            )
            await response(scope, receive, send)
            return

        # Add validation result to request state
        scope["validation_result"] = validation_result

        # Continue with the request
        await self.app(scope, receive, send)

    async def _validate_request(self, request: Request) -> ValidationResult:
        """Validate an incoming request."""
        errors = []
        warnings = []

        # Validate request method
        if request.method not in ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]:
            warnings.append(f"Unusual HTTP method: {request.method}")

        # Validate path
        if len(request.url.path) > 500:
            errors.append("Request path too long")

        # Validate query parameters
        for key, value in request.query_params.items():
            if len(key) > 100:
                errors.append(f"Query parameter name too long: {key}")
            if len(value) > 1000:
                errors.append(f"Query parameter value too long: {key}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )