import secrets
import hashlib
import bcrypt
from cryptography.fernet import Fernet
from src.config import settings
import base64

class SecurityUtils:
    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(length)

    @staticmethod
    def hash_sensitive_data(data: str) -> str:
        """Hash sensitive data for storage"""
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def verify_data_hash(data: str, hash_value: str) -> bool:
        """Verify data against its hash"""
        return hashlib.sha256(data.encode()).hexdigest() == hash_value

    @staticmethod
    def encrypt_sensitive_data(data: str) -> str:
        """Encrypt sensitive data for storage"""
        # Generate encryption key from JWT secret
        key = base64.urlsafe_b64encode(settings.JWT_SECRET_KEY.encode()[:32].ljust(32, b'0'))
        fernet = Fernet(key)
        return fernet.encrypt(data.encode()).decode()

    @staticmethod
    def decrypt_sensitive_data(encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        key = base64.urlsafe_b64encode(settings.JWT_SECRET_KEY.encode()[:32].ljust(32, b'0'))
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_data.encode()).decode()

class PasswordManager:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

class InputValidator:
    @staticmethod
    def is_safe_path(path: str) -> bool:
        """Check if path is safe and doesn't contain directory traversal"""
        return not ('..' in path or path.startswith('/') or ':' in path)

    @staticmethod
    def is_safe_command(command: str) -> bool:
        """Check if command is safe to execute"""
        dangerous_commands = ['rm ', 'del ', 'format ', 'mkfs ', 'dd ']
        return not any(danger in command.lower() for danger in dangerous_commands)

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        # Remove path separators and dangerous characters
        sanitized = filename.replace('/', '_').replace('\\', '_')
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c in '._- ')
        return sanitized.strip()

class RateLimiter:
    def __init__(self, max_calls: int = 60, window_seconds: int = 60):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls = {}

    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed based on rate limit"""
        import time

        current_time = time.time()

        # Clean up old calls
        if identifier in self.calls:
            self.calls[identifier] = [
                call_time for call_time in self.calls[identifier]
                if current_time - call_time < self.window_seconds
            ]

        # Check if limit exceeded
        if identifier not in self.calls:
            self.calls[identifier] = []

        if len(self.calls[identifier]) >= self.max_calls:
            return False

        # Record this call
        self.calls[identifier].append(current_time)
        return True

class AuditLogger:
    def __init__(self):
        self.logs = []

    def log_security_event(self, event_type: str, user_id: int = None, details: dict = None):
        """Log security events for auditing"""
        import time

        log_entry = {
            'timestamp': time.time(),
            'event_type': event_type,
            'user_id': user_id,
            'details': details or {}
        }

        self.logs.append(log_entry)

        # In production, you'd want to persist this to a database
        # For now, we'll keep it in memory
        if len(self.logs) > 1000:  # Keep only last 1000 entries
            self.logs = self.logs[-1000:]

    def get_security_logs(self, user_id: int = None, limit: int = 100) -> list:
        """Get security logs, optionally filtered by user"""
        logs = self.logs
        if user_id:
            logs = [log for log in logs if log.get('user_id') == user_id]

        return logs[-limit:] if limit else logs

# Initialize audit logger
audit_logger = AuditLogger()