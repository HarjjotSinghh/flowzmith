from typing import Dict, Any, Optional
import re
from pydantic import validator, EmailStr
from pydantic import BaseModel

class ContractValidator:
    @staticmethod
    def validate_cadence_contract(contract_code: str) -> Dict[str, Any]:
        """Validate Cadence smart contract syntax and structure"""
        errors = []
        warnings = []

        # Basic syntax checks
        if not contract_code.strip():
            errors.append("Contract code cannot be empty")

        # Check for required Cadence keywords
        required_keywords = ['pub', 'contract', 'let', 'fun']
        for keyword in required_keywords:
            if keyword not in contract_code:
                warnings.append(f"Missing keyword: {keyword}")

        # Check for proper contract structure
        if 'contract' not in contract_code:
            errors.append("No contract definition found")

        # Check for resource management
        if 'resource' not in contract_code:
            warnings.append("No resources defined - consider using resources for asset management")

        # Check for access control
        if 'access(' not in contract_code:
            warnings.append("No access control defined - consider adding access modifiers")

        # Check for error handling
        if 'panic' not in contract_code and 'pre' not in contract_code:
            warnings.append("No error handling found - consider adding pre-conditions")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    @staticmethod
    def validate_flow_address(address: str) -> bool:
        """Validate Flow blockchain address format"""
        pattern = r'^0x[a-fA-F0-9]{16}$'
        return bool(re.match(pattern, address))

    @staticmethod
    def validate_network(network: str) -> bool:
        """Validate network name"""
        valid_networks = ['testnet', 'mainnet', 'emulator']
        return network.lower() in valid_networks

class UserValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength"""
        errors = []

        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")

        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")

        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")

        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")

        return {
            "is_strong": len(errors) == 0,
            "errors": errors
        }

    @staticmethod
    def validate_persona_type(persona_type: str) -> bool:
        """Validate user persona type"""
        valid_personas = ['DEVELOPER', 'DESIGNER', 'PRODUCT_MANAGER', 'BUSINESS_ANALYST']
        return persona_type.upper() in valid_personas

class InputSanitizer:
    @staticmethod
    def sanitize_string(input_string: str) -> str:
        """Sanitize string input to prevent injection attacks"""
        # Remove potentially dangerous characters
        sanitized = input_string.strip()
        sanitized = re.sub(r'[<>"\']', '', sanitized)
        sanitized = re.sub(r'\s+', ' ', sanitized)  # Normalize whitespace
        return sanitized

    @staticmethod
    def sanitize_json_input(json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize JSON input"""
        sanitized = {}
        for key, value in json_data.items():
            if isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = InputSanitizer.sanitize_json_input(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    InputSanitizer.sanitize_json_input(item) if isinstance(item, dict)
                    else InputSanitizer.sanitize_string(item) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        return sanitized

# Pydantic models for validation
class ContractRequest(BaseModel):
    input_type: str
    content: str
    pre_conditions: Optional[Dict[str, Any]] = None
    post_conditions: Optional[Dict[str, Any]] = None
    network: str = "testnet"

    @validator('input_type')
    def validate_input_type(cls, v):
        if v not in ['NATURAL_LANGUAGE', 'FILE_UPLOAD']:
            raise ValueError('input_type must be NATURAL_LANGUAGE or FILE_UPLOAD')
        return v

    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('content cannot be empty')
        return InputSanitizer.sanitize_string(v)

    @validator('network')
    def validate_network(cls, v):
        if not ContractValidator.validate_network(v):
            raise ValueError('network must be testnet, mainnet, or emulator')
        return v

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    persona_type: str

    @validator('password')
    def validate_password(cls, v):
        validation = UserValidator.validate_password_strength(v)
        if not validation['is_strong']:
            raise ValueError(f'Password too weak: {", ".join(validation["errors"])}')
        return v

    @validator('persona_type')
    def validate_persona_type(cls, v):
        if not UserValidator.validate_persona_type(v):
            raise ValueError('persona_type must be DEVELOPER, DESIGNER, PRODUCT_MANAGER, or BUSINESS_ANALYST')
        return v

    @validator('full_name')
    def validate_full_name(cls, v):
        if not v or not v.strip():
            raise ValueError('full_name cannot be empty')
        return InputSanitizer.sanitize_string(v)