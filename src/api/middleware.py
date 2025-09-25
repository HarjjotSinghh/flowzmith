"""
Middleware for Smart Contract LLM Builder API.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
import jwt
import hashlib
import secrets

from ..models.database import get_db
from ..models import User
from ..schemas import ErrorResponse
from ..config import get_settings

logger = logging.getLogger(__name__)

security = HTTPBearer()


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for handling JWT authentication."""

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """Process authentication for incoming requests."""
        # Log the request path for debugging
        logger.info(f"AuthenticationMiddleware: Processing request to {request.url.path}")
        
        # Skip authentication for certain paths
        if self._should_skip_auth(request.url.path):
            logger.info(f"AuthenticationMiddleware: Skipping auth for {request.url.path}")
            return await call_next(request)

        try:
            # Get authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing or invalid authorization header"
                )

            token = auth_header.split(" ")[1]

            # Verify JWT token
            payload = self._verify_token(token)

            # Add user info to request state
            request.state.user_id = payload.get("user_id")
            request.state.user_email = payload.get("email")
            request.state.user_role = payload.get("role", "user")

            # Add database session to request
            request.state.db = next(get_db())

            # Verify user exists and is active
            user = request.state.db.query(User).filter(
                User.id == request.state.user_id
            ).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is inactive"
                )

            # Update last login
            user.last_login = datetime.utcnow()
            request.state.db.commit()

            response = await call_next(request)

            # Clean up database session
            request.state.db.close()

            return response

        except HTTPException:
            raise
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal authentication error"
            )

    def _should_skip_auth(self, path: str) -> bool:
        """Check if authentication should be skipped for this path."""
        skip_paths = [
            "/",
            "/favicon.ico",
            "/health",
            "/users/login",
            "/users",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/ws/",
            "/ws",
            "/ws/",
            "/ws",
            "/static/"
        ]

        should_skip = any(path.startswith(skip_path) for skip_path in skip_paths)
        logger.info(f"AuthenticationMiddleware: Path '{path}' should skip auth: {should_skip}")
        logger.info(f"AuthenticationMiddleware: Skip paths: {skip_paths}")
        
        return should_skip

    def _verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload."""
        settings = get_settings()
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""

    def __init__(self, app):
        super().__init__(app)
        self.request_counts: Dict[str, Dict[str, int]] = {}
        self.rate_limits = {
            "/api/contracts": 10,  # 10 requests per minute
            "/api/deployments": 5,  # 5 requests per minute
            "/api/transactions": 20,  # 20 requests per minute
            "/default": 100  # 100 requests per minute for other endpoints
        }

    async def dispatch(self, request: Request, call_next):
        """Process rate limiting for incoming requests."""
        try:
            # Skip rate limiting for WebSocket endpoints
            if request.url.path.startswith("/ws"):
                logger.info(f"RateLimitMiddleware: Skipping rate limit for {request.url.path}")
                return await call_next(request)

            # Get client identifier
            client_id = self._get_client_id(request)

            # Get rate limit for this endpoint
            endpoint = self._get_endpoint_key(request.url.path)
            limit = self.rate_limits.get(endpoint, self.rate_limits["default"])

            # Check and update rate limit
            if not self._check_rate_limit(client_id, endpoint, limit):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )

            response = await call_next(request)
            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return await call_next(request)  # Fail open

    def _get_client_id(self, request: Request) -> str:
        """Get a unique identifier for the client."""
        # Try to get user ID from request state
        if hasattr(request.state, 'user_id'):
            return f"user_{request.state.user_id}"

        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        return request.client.host

    def _get_endpoint_key(self, path: str) -> str:
        """Get the rate limit key for an endpoint."""
        if path.startswith("/api/contracts"):
            return "/api/contracts"
        elif path.startswith("/api/deployments"):
            return "/api/deployments"
        elif path.startswith("/api/transactions"):
            return "/api/transactions"
        else:
            return "/default"

    def _check_rate_limit(self, client_id: str, endpoint: str, limit: int) -> bool:
        """Check if the client has exceeded the rate limit."""
        now = datetime.utcnow()
        minute_key = now.strftime("%Y-%m-%d-%H-%M")

        if client_id not in self.request_counts:
            self.request_counts[client_id] = {}

        if endpoint not in self.request_counts[client_id]:
            self.request_counts[client_id][endpoint] = {}

        if minute_key not in self.request_counts[client_id][endpoint]:
            self.request_counts[client_id][endpoint][minute_key] = 0

        # Clean up old entries
        self._cleanup_old_entries(client_id, endpoint)

        # Check current count
        current_count = self.request_counts[client_id][endpoint][minute_key]
        if current_count >= limit:
            return False

        # Increment count
        self.request_counts[client_id][endpoint][minute_key] += 1
        return True

    def _cleanup_old_entries(self, client_id: str, endpoint: str):
        """Clean up old rate limit entries."""
        now = datetime.utcnow()
        cutoff_time = now - timedelta(minutes=5)  # Keep 5 minutes of data

        if client_id in self.request_counts and endpoint in self.request_counts[client_id]:
            to_remove = []
            for minute_key in self.request_counts[client_id][endpoint]:
                minute_time = datetime.strptime(minute_key, "%Y-%m-%d-%H-%M")
                if minute_time < cutoff_time:
                    to_remove.append(minute_key)

            for minute_key in to_remove:
                del self.request_counts[client_id][endpoint][minute_key]


class ValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for request validation."""

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """Validate incoming requests."""
        try:
            # Skip validation for WebSocket endpoints
            if self._should_skip_validation(request.url.path):
                logger.info(f"ValidationMiddleware: Skipping validation for {request.url.path}")
                return await call_next(request)

            # Validate content type for POST/PUT/PATCH requests
            if request.method in ["POST", "PUT", "PATCH"]:
                self._validate_content_type(request)

            # Validate request size
            self._validate_request_size(request)

            response = await call_next(request)
            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request"
            )

    def _should_skip_validation(self, path: str) -> bool:
        """Check if validation should be skipped for this path."""
        skip_paths = [
            "/ws/",
            "/ws"
        ]
        should_skip = any(path.startswith(skip_path) for skip_path in skip_paths)
        logger.info(f"ValidationMiddleware: Path '{path}' should skip validation: {should_skip}")
        return should_skip

    def _validate_content_type(self, request: Request):
        """Validate content type for requests with body."""
        content_type = request.headers.get("content-type", "")

        # Skip validation for WebSocket upgrades
        if "websocket" in content_type.lower():
            return

        # For API requests, expect JSON except specific multipart endpoints
        if request.url.path.startswith("/api/"):
            # Allow file upload endpoints to use multipart/form-data
            multipart_allowed_paths = [
                "/api/v1/contracts/file",
                "/api/v1/documentation/upload"
            ]

            is_multipart = content_type.startswith("multipart/form-data")
            is_allowed_multipart_path = any(request.url.path.startswith(p) for p in multipart_allowed_paths)

            if not is_multipart and not content_type.startswith("application/json"):
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail="Content-Type must be application/json"
                )

            if is_multipart and not is_allowed_multipart_path:
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail="Multipart upload only allowed on upload endpoints"
                )

    def _validate_request_size(self, request: Request):
        """Validate request size."""
        content_length = request.headers.get("content-length")
        if content_length:
            size_mb = int(content_length) / (1024 * 1024)
            if size_mb > 10:  # 10MB limit
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Request too large"
                )


class CORSMiddleware(BaseHTTPMiddleware):
    """Middleware for handling CORS."""

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """Handle CORS headers."""
        response = await call_next(request)

        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers."""

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """Add security headers to responses."""
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging."""

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """Log incoming requests."""
        start_time = datetime.utcnow()

        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")

        response = await call_next(request)

        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()

        # Log response
        logger.info(
            f"Response: {response.status_code} "
            f"({duration:.3f}s) "
            f"{request.method} {request.url.path}"
        )

        return response


class JWTTokenManager:
    """Utility class for JWT token management."""

    @staticmethod
    def create_token(user_id: str, email: str, role: str = "user") -> str:
        """Create a JWT token."""
        settings = get_settings()
        payload = {
            "user_id": user_id,
            "email": email,
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(32)
        }

        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token."""
        settings = get_settings()
        try:
            return jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """Create a refresh token."""
        return hashlib.sha256(f"{user_id}:{secrets.token_urlsafe(32)}:{datetime.utcnow().isoformat()}".encode()).hexdigest()


# Dependency for getting current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    try:
        token = credentials.credentials
        payload = JWTTokenManager.verify_token(token)

        user_id = payload.get("user_id")
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal authentication error"
        )


# Dependency for getting current user ID
async def get_current_user_id(
    user: User = Depends(get_current_user)
) -> str:
    """Get current user ID."""
    return str(user.id)


# Error response formatter
def create_error_response(
    error: str,
    message: str,
    status_code: int = 500,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a standardized error response."""
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error=error,
            message=message,
            status_code=status_code,
            details=details,
            timestamp=datetime.utcnow()
        ).dict()
    )