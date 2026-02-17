from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Optional


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    """

    def __init__(self, app, hsts_max_age: int = 31536000, csp_policy: Optional[str] = None):
        super().__init__(app)
        self.hsts_max_age = hsts_max_age
        self.csp_policy = csp_policy or (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = f"max-age={self.hsts_max_age}; includeSubDomains; preload"
        response.headers["Content-Security-Policy"] = self.csp_policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"

        # Remove server header to hide server information
        response.headers.pop("server", None)

        return response


class SecureHeadersMiddleware(BaseHTTPMiddleware):
    """
    Enhanced security headers middleware with more comprehensive protection.
    """

    def __init__(
        self,
        app,
        hsts_max_age: int = 31536000,
        include_hsts_subdomains: bool = True,
        hsts_preload: bool = True,
        csp_policy: Optional[str] = None,
        force_https_redirect: bool = False
    ):
        super().__init__(app)
        self.hsts_max_age = hsts_max_age
        self.include_hsts_subdomains = include_hsts_subdomains
        self.hsts_preload = hsts_preload
        self.csp_policy = csp_policy or (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://api.example.com; "  # Replace with actual API endpoints
            "frame-ancestors 'none'; "
            "object-src 'none'; "
            "base-uri 'self';"
        )
        self.force_https_redirect = force_https_redirect

    async def dispatch(self, request: Request, call_next):
        # Force HTTPS redirect if enabled
        if self.force_https_redirect and request.url.scheme == "http":
            https_url = str(request.url).replace("http://", "https://", 1)
            return Response(
                status_code=301,
                headers={"Location": https_url}
            )

        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"  # Or "SAMEORIGIN" if you need same-origin frames
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Build HSTS header
        hsts_value = f"max-age={self.hsts_max_age}"
        if self.include_hsts_subdomains:
            hsts_value += "; includeSubDomains"
        if self.hsts_preload:
            hsts_value += "; preload"
        response.headers["Strict-Transport-Security"] = hsts_value

        response.headers["Content-Security-Policy"] = self.csp_policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), "
            "ambient-light-sensor=(), "
            "autoplay=(), "
            "battery=(), "
            "camera=(), "
            "display-capture=(), "
            "document-domain=(), "
            "encrypted-media=(), "
            "execution-while-not-rendered=(), "
            "execution-while-out-of-viewport=(), "
            "fullscreen=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "midi=(), "
            "navigation-override=(), "
            "payment=(), "
            "picture-in-picture=(), "
            "pointer-lock=(), "
            "screen-wake-lock=(), "
            "sync-xhr=(), "
            "usb=(), "
            "web-share=(), "
            "xr-spatial-tracking=()"
        )
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"

        # Remove information revealing headers
        response.headers.pop("server", None)  # Remove server header
        response.headers.pop("x-powered-by", None)  # Remove if FastAPI adds it

        # Add feature policy (deprecated but still supported by some browsers)
        response.headers["Feature-Policy"] = (
            "geolocation 'none'; "
            "microphone 'none'; "
            "camera 'none'"
        )

        return response


def add_security_headers(app, **kwargs):
    """
    Helper function to add security headers middleware to the application.

    Args:
        app: FastAPI application instance
        **kwargs: Additional arguments for the security middleware
    """
    app.add_middleware(SecureHeadersMiddleware, **kwargs)