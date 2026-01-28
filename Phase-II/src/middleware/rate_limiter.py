from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from collections import defaultdict
from datetime import datetime, timedelta
import time
import asyncio
from typing import Dict, Tuple
import hashlib

# For production use, you'd want to use Redis or similar for distributed rate limiting
# This implementation uses in-memory storage which is suitable for single-server deployments


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    pass


class InMemoryRateLimiter:
    """
    In-memory rate limiter that tracks requests by key and window.
    """

    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int]:
        """
        Check if a request is allowed based on rate limits.

        Args:
            key: Unique identifier for the rate limit (e.g., IP address)
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds

        Returns:
            Tuple of (is_allowed: bool, remaining_requests: int)
        """
        now = datetime.now()
        window_start = now - timedelta(seconds=window_seconds)

        # Clean old requests outside the window
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]

        current_count = len(self.requests[key])

        if current_count >= max_requests:
            # Calculate seconds until reset
            oldest_req = min(self.requests[key]) if self.requests[key] else now
            seconds_until_reset = int((oldest_req + timedelta(seconds=window_seconds) - now).total_seconds())
            return False, max(0, max_requests - current_count), seconds_until_reset

        # Add current request
        self.requests[key].append(now)

        return True, max(0, max_requests - current_count - 1), 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to implement rate limiting for API endpoints.
    """

    def __init__(self, app, default_limits=None):
        super().__init__(app)
        self.rate_limiter = InMemoryRateLimiter()

        # Default rate limits (requests per window)
        self.default_limits = default_limits or {
            "global": {"max_requests": 1000, "window_seconds": 3600},  # 1000 requests per hour globally
            "per_ip": {"max_requests": 100, "window_seconds": 3600},   # 100 requests per hour per IP
            "per_endpoint": {"max_requests": 10, "window_seconds": 60}, # 10 requests per minute per endpoint
        }

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()

        return request.client.host

    def _get_endpoint_key(self, request: Request) -> str:
        """Generate a key for the endpoint."""
        return f"endpoint:{request.method}:{request.url.path}"

    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        endpoint_key = self._get_endpoint_key(request)

        # Check global rate limit
        try:
            global_allowed, global_remaining, global_reset = self.rate_limiter.is_allowed(
                "global",
                self.default_limits["global"]["max_requests"],
                self.default_limits["global"]["window_seconds"]
            )

            if not global_allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "RATE_LIMIT_EXCEEDED",
                        "message": "Global rate limit exceeded",
                        "retry_after": global_reset
                    }
                )

            # Check per-IP rate limit
            ip_allowed, ip_remaining, ip_reset = self.rate_limiter.is_allowed(
                f"ip:{client_ip}",
                self.default_limits["per_ip"]["max_requests"],
                self.default_limits["per_ip"]["window_seconds"]
            )

            if not ip_allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "RATE_LIMIT_EXCEEDED",
                        "message": "Rate limit exceeded for your IP address",
                        "retry_after": ip_reset
                    }
                )

            # Check per-endpoint rate limit
            endpoint_allowed, endpoint_remaining, endpoint_reset = self.rate_limiter.is_allowed(
                endpoint_key,
                self.default_limits["per_endpoint"]["max_requests"],
                self.default_limits["per_endpoint"]["window_seconds"]
            )

            if not endpoint_allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit exceeded for {request.method} {request.url.path}",
                        "retry_after": endpoint_reset
                    }
                )

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Log the error but don't break the request
            print(f"Rate limiter error: {e}")

        # Add rate limit headers to response
        response = await call_next(request)

        # Add rate limit information to response headers
        _, global_remaining, _ = self.rate_limiter.is_allowed(
            "global",
            self.default_limits["global"]["max_requests"],
            self.default_limits["global"]["window_seconds"]
        )

        _, ip_remaining, _ = self.rate_limiter.is_allowed(
            f"ip:{client_ip}",
            self.default_limits["per_ip"]["max_requests"],
            self.default_limits["per_ip"]["window_seconds"]
        )

        _, endpoint_remaining, _ = self.rate_limiter.is_allowed(
            endpoint_key,
            self.default_limits["per_endpoint"]["max_requests"],
            self.default_limits["per_endpoint"]["window_seconds"]
        )

        response.headers["X-RateLimit-Global-Remaining"] = str(global_remaining)
        response.headers["X-RateLimit-IP-Remaining"] = str(ip_remaining)
        response.headers["X-RateLimit-Endpoint-Remaining"] = str(endpoint_remaining)

        return response


# Alternative implementation using specific rate limits per endpoint
def get_rate_limit_key(request: Request) -> str:
    """Generate a rate limit key based on the request."""
    client_ip = request.headers.get("x-forwarded-for", request.client.host).split(",")[0]
    return f"{client_ip}:{request.url.path}:{request.method}"


def create_rate_limit_middleware(max_requests: int = 10, window_seconds: int = 60):
    """
    Factory function to create a rate limit middleware with custom limits.

    Args:
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds

    Returns:
        RateLimitMiddleware: Configured rate limit middleware
    """
    rate_limiter = InMemoryRateLimiter()

    class CustomRateLimitMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            key = get_rate_limit_key(request)

            try:
                allowed, remaining, reset = rate_limiter.is_allowed(key, max_requests, window_seconds)

                if not allowed:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail={
                            "error": "RATE_LIMIT_EXCEEDED",
                            "message": "Too many requests",
                            "retry_after": reset
                        }
                    )

            except HTTPException:
                raise
            except Exception:
                pass  # Don't break the request if rate limiter fails

            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(max_requests)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset)

            return response

    return CustomRateLimitMiddleware