from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from src.config import settings
import time
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.call_timestamps = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        # Clean up old timestamps (older than 1 minute)
        if client_ip in self.call_timestamps:
            self.call_timestamps[client_ip] = [
                timestamp for timestamp in self.call_timestamps[client_ip]
                if current_time - timestamp < 60
            ]

        # Check if rate limit exceeded
        if client_ip in self.call_timestamps and len(self.call_timestamps[client_ip]) >= self.calls_per_minute:
            return Response(
                content="Rate limit exceeded",
                status_code=429,
                media_type="text/plain"
            )

        # Record this call
        if client_ip not in self.call_timestamps:
            self.call_timestamps[client_ip] = []
        self.call_timestamps[client_ip].append(current_time)

        response = await call_next(request)
        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        logger.info(f"Request: {request.method} {request.url}")

        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} - {process_time:.4f}s")

        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response