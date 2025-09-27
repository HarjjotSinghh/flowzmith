"""
Custom exceptions and error handling for Flowzmith.
"""

import logging
import traceback
from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from src.schemas import ErrorResponse

logger = logging.getLogger(__name__)


class SmartContractError(Exception):
    """Base exception for Flowzmith."""

    def __init__(
        self,
        message: str,
        error_code: str = "SMART_CONTRACT_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(SmartContractError):
    """Authentication related errors."""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTH_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class AuthorizationError(SmartContractError):
    """Authorization related errors."""

    def __init__(self, message: str = "Authorization failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHZ_ERROR",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class ValidationError(SmartContractError):
    """Validation related errors."""

    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class NotFoundError(SmartContractError):
    """Resource not found errors."""

    def __init__(self, message: str = "Resource not found", resource_type: str = None, resource_id: str = None):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id

        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class ConflictError(SmartContractError):
    """Resource conflict errors."""

    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class RateLimitError(SmartContractError):
    """Rate limiting errors."""

    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


class ConfigurationError(SmartContractError):
    """Configuration related errors."""

    def __init__(self, message: str = "Configuration error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class LLMError(SmartContractError):
    """LLM provider related errors."""

    def __init__(self, message: str = "LLM error", provider: str = None, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        if provider:
            error_details["provider"] = provider

        super().__init__(
            message=message,
            error_code="LLM_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=error_details
        )


class FlowError(SmartContractError):
    """Flow blockchain related errors."""

    def __init__(self, message: str = "Flow error", operation: str = None, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        if operation:
            error_details["operation"] = operation

        super().__init__(
            message=message,
            error_code="FLOW_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=error_details
        )


class DatabaseError(SmartContractError):
    """Database related errors."""

    def __init__(self, message: str = "Database error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DB_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


class DataControlError(SmartContractError):
    """Data control and privacy related errors."""

    def __init__(self, message: str = "Data control error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DATA_CONTROL_ERROR",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class ErrorHandler:
    """Centralized error handling for the application."""

    def __init__(self):
        self.error_mappings = {
            AuthenticationError: self._handle_authentication_error,
            AuthorizationError: self._handle_authorization_error,
            ValidationError: self._handle_validation_error,
            NotFoundError: self._handle_not_found_error,
            ConflictError: self._handle_conflict_error,
            RateLimitError: self._handle_rate_limit_error,
            ConfigurationError: self._handle_configuration_error,
            LLMError: self._handle_llm_error,
            FlowError: self._handle_flow_error,
            DatabaseError: self._handle_database_error,
            DataControlError: self._handle_data_control_error,
        }

    def handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle any exception and return appropriate response."""
        try:
            # Log the error
            self._log_error(request, exc)

            # Handle known error types
            if isinstance(exc, SmartContractError):
                handler = self.error_mappings.get(type(exc), self._handle_generic_error)
                return handler(request, exc)

            # Handle FastAPI/Starlette HTTP exceptions
            if isinstance(exc, (HTTPException, StarletteHTTPException)):
                return self._handle_http_exception(request, exc)

            # Handle validation errors
            if isinstance(exc, (RequestValidationError, ValidationError)):
                return self._handle_request_validation_error(request, exc)

            # Handle SQLAlchemy errors
            if isinstance(exc, SQLAlchemyError):
                return self._handle_sqlalchemy_error(request, exc)

            # Handle all other exceptions
            return self._handle_generic_error(request, exc)

        except Exception as handler_error:
            # Fallback if error handler itself fails
            logger.error(f"Error handler failed: {handler_error}")
            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    error="INTERNAL_ERROR",
                    message="Internal server error",
                    status_code=500,
                    details={"handler_error": str(handler_error)},
                    timestamp=datetime.utcnow().isoformat()
                ).dict()
            )

    def _log_error(self, request: Request, exc: Exception):
        """Log error with context."""
        error_details = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "request_method": request.method,
            "request_url": str(request.url),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }

        # Add request details for debugging
        if hasattr(request.state, 'user_id'):
            error_details["user_id"] = request.state.user_id

        logger.error(
            f"Unhandled exception: {exc}",
            extra=error_details,
            exc_info=True
        )

    def _handle_authentication_error(self, request: Request, exc: AuthenticationError) -> JSONResponse:
        """Handle authentication errors."""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.error_code,
                message=exc.message,
                status_code=exc.status_code,
                details=exc.details,
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )

    def _handle_authorization_error(self, request: Request, exc: AuthorizationError) -> JSONResponse:
        """Handle authorization errors."""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.error_code,
                message=exc.message,
                status_code=exc.status_code,
                details=exc.details,
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )

    def _handle_validation_error(self, request: Request, exc: ValidationError) -> JSONResponse:
        """Handle validation errors."""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.error_code,
                message=exc.message,
                status_code=exc.status_code,
                details=exc.details,
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )

    def _handle_not_found_error(self, request: Request, exc: NotFoundError) -> JSONResponse:
        """Handle not found errors."""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.error_code,
                message=exc.message,
                status_code=exc.status_code,
                details=exc.details,
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )

    def _handle_conflict_error(self, request: Request, exc: ConflictError) -> JSONResponse:
        """Handle conflict errors."""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.error_code,
                message=exc.message,
                status_code=exc.status_code,
                details=exc.details,
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )

    def _handle_rate_limit_error(self, request: Request, exc: RateLimitError) -> JSONResponse:
        """Handle rate limit errors."""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.error_code,
                message=exc.message,
                status_code=exc.status_code,
                details=exc.details,
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )

    def _handle_configuration_error(self, request: Request, exc: ConfigurationError) -> JSONResponse:
        """Handle configuration errors."""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.error_code,
                message=exc.message,
                status_code=exc.status_code,
                details=exc.details,
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )

    def _handle_llm_error(self, request: Request, exc: LLMError) -> JSONResponse:
        """Handle LLM errors."""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.error_code,
                message=exc.message,
                status_code=exc.status_code,
                details=exc.details,
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )

    def _handle_flow_error(self, request: Request, exc: FlowError) -> JSONResponse:
        """Handle Flow errors."""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.error_code,
                message=exc.message,
                status_code=exc.status_code,
                details=exc.details,
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )

    def _handle_database_error(self, request: Request, exc: DatabaseError) -> JSONResponse:
        """Handle database errors."""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.error_code,
                message=exc.message,
                status_code=exc.status_code,
                details=exc.details,
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )

    def _handle_data_control_error(self, request: Request, exc: DataControlError) -> JSONResponse:
        """Handle data control errors."""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.error_code,
                message=exc.message,
                status_code=exc.status_code,
                details=exc.details,
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )

    def _handle_http_exception(self, request: Request, exc: HTTPException) -> JSONResponse:
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error="HTTP_ERROR",
                message=exc.detail,
                status_code=exc.status_code,
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )

    def _handle_request_validation_error(self, request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle request validation errors."""
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error="VALIDATION_ERROR",
                message="Request validation failed",
                status_code=422,
                details={
                    "validation_errors": [
                        {
                            "field": ".".join(str(loc) for loc in error["loc"]),
                            "message": error["msg"],
                            "type": error["type"]
                        }
                        for error in exc.errors()
                    ]
                },
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )

    def _handle_sqlalchemy_error(self, request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """Handle SQLAlchemy errors."""
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="DATABASE_ERROR",
                message="Database operation failed",
                status_code=500,
                details={
                    "error_type": type(exc).__name__,
                    "error_message": str(exc)
                },
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )

    def _handle_generic_error(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle generic exceptions with detailed error information."""
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Internal Server Error",
                message="An unexpected error occurred. Please try again later.",
                status_code=500,
                timestamp=datetime.utcnow().isoformat()
            ).dict()
        )


# Global error handler instance
error_handler = ErrorHandler()


# Exception handlers for FastAPI app
async def smart_contract_exception_handler(request: Request, exc: SmartContractError):
    """Handler for SmartContractError exceptions."""
    return error_handler.handle_exception(request, exc)


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler for HTTPException exceptions."""
    return error_handler.handle_exception(request, exc)


async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler for RequestValidationError exceptions."""
    return error_handler.handle_exception(request, exc)


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handler for SQLAlchemyError exceptions."""
    return error_handler.handle_exception(request, exc)


async def general_exception_handler(request: Request, exc: Exception):
    """Handler for general exceptions."""
    return error_handler.handle_exception(request, exc)


# Error response utilities
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
            timestamp=datetime.utcnow().isoformat()
        ).dict()
    )


def log_and_raise_error(
    error_class: type,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    **kwargs
):
    """Log an error and raise the appropriate exception."""
    logger.error(f"{error_class.__name__}: {message}")
    raise error_class(message=message, details=details, **kwargs)