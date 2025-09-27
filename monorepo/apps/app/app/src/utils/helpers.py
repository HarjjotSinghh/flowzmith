import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os
import logging

logger = logging.getLogger(__name__)

class IDGenerator:
    @staticmethod
    def generate_submission_id() -> str:
        """Generate unique submission ID"""
        return f"sub_{uuid.uuid4().hex[:12]}"

    @staticmethod
    def generate_deployment_id() -> str:
        """Generate unique deployment ID"""
        return f"dep_{uuid.uuid4().hex[:12]}"

    @staticmethod
    def generate_config_id() -> str:
        """Generate unique configuration ID"""
        return f"cfg_{uuid.uuid4().hex[:12]}"

class DateTimeUtils:
    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """Format datetime for API response"""
        return dt.isoformat() if dt else None

    @staticmethod
    def parse_datetime(dt_str: str) -> Optional[datetime]:
        """Parse datetime from string"""
        try:
            return datetime.fromisoformat(dt_str)
        except ValueError:
            return None

    @staticmethod
    def get_time_ago(dt: datetime) -> str:
        """Get human-readable time ago string"""
        now = datetime.utcnow()
        diff = now - dt

        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "just now"

class FileUtils:
    @staticmethod
    def ensure_directory_exists(path: str):
        """Ensure directory exists, create if not"""
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension from filename"""
        return os.path.splitext(filename)[1].lower()

    @staticmethod
    def is_valid_contract_file(filename: str) -> bool:
        """Check if file is a valid contract file"""
        valid_extensions = ['.cdc', '.sol']
        return FileUtils.get_file_extension(filename) in valid_extensions

    @staticmethod
    def read_file_safely(file_path: str) -> Optional[str]:
        """Read file safely with error handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            return None

    @staticmethod
    def write_file_safely(file_path: str, content: str) -> bool:
        """Write file safely with error handling"""
        try:
            FileUtils.ensure_directory_exists(os.path.dirname(file_path))
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {str(e)}")
            return False

class NetworkUtils:
    @staticmethod
    def get_flow_network_config(network: str) -> Dict[str, Any]:
        """Get Flow network configuration"""
        configs = {
            'mainnet': {
                'host': 'access.mainnet.nodes.onflow.org',
                'port': 9000,
                'chain_id': 'flow-mainnet'
            },
            'testnet': {
                'host': 'access.devnet.nodes.onflow.org',
                'port': 9000,
                'chain_id': 'flow-testnet'
            },
            'emulator': {
                'host': '127.0.0.1',
                'port': 3569,
                'chain_id': 'flow-emulator'
            }
        }
        return configs.get(network.lower(), configs['testnet'])

class ValidationUtils:
    @staticmethod
    def is_valid_json(json_str: str) -> bool:
        """Check if string is valid JSON"""
        try:
            json.loads(json_str)
            return True
        except json.JSONDecodeError:
            return False

    @staticmethod
    def safe_json_loads(json_str: str) -> Optional[Dict[str, Any]]:
        """Safely load JSON string"""
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """Validate that all required fields are present"""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        return missing_fields

class ResponseFormatter:
    @staticmethod
    def success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
        """Format success response"""
        return {
            "success": True,
            "message": message,
            "data": data
        }

    @staticmethod
    def error_response(message: str, error_code: str = "ERROR", details: Any = None) -> Dict[str, Any]:
        """Format error response"""
        return {
            "success": False,
            "message": message,
            "error_code": error_code,
            "details": details
        }

    @staticmethod
    def paginated_response(items: List[Any], total: int, page: int, page_size: int) -> Dict[str, Any]:
        """Format paginated response"""
        return {
            "success": True,
            "data": items,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        }

class ConfigUtils:
    @staticmethod
    def get_config_value(key: str, default: Any = None) -> Any:
        """Get configuration value from environment or default"""
        return os.getenv(key, default)

    @staticmethod
    def get_bool_config(key: str, default: bool = False) -> bool:
        """Get boolean configuration value"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')

    @staticmethod
    def get_int_config(key: str, default: int = 0) -> int:
        """Get integer configuration value"""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default

class StringUtils:
    @staticmethod
    def truncate_string(text: str, max_length: int = 100) -> str:
        """Truncate string to maximum length"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace in string"""
        return ' '.join(text.split())

    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction - in production, use NLP libraries
        words = text.lower().split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}

        keywords = []
        for word in words:
            if len(word) > 3 and word not in stop_words:
                keywords.append(word)
            if len(keywords) >= max_keywords:
                break

        return keywords