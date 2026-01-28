from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.exceptions import HTTPException
from typing import Optional, Dict, Any
import json
import re
from src.utils.sanitize import sanitize_input, clean_user_input


class InputValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate and sanitize incoming request data.
    """

    def __init__(self, app, max_body_size: int = 1024 * 1024):  # 1MB default
        super().__init__(app)
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next):
        # Get the request body if it's a POST, PUT, or PATCH request
        if request.method in ["POST", "PUT", "PATCH"]:
            # Check content length header if available
            content_length = request.headers.get("content-length")
            if content_length:
                try:
                    if int(content_length) > self.max_body_size:
                        raise HTTPException(
                            status_code=413,
                            detail="Request body too large"
                        )
                except ValueError:
                    # If content-length header is malformed, continue with validation
                    pass

            # Read and validate the request body
            try:
                body_bytes = await request.body()

                if body_bytes:
                    # Check if body size exceeds limit
                    if len(body_bytes) > self.max_body_size:
                        raise HTTPException(
                            status_code=413,
                            detail="Request body too large"
                        )

                    # Only validate JSON content
                    content_type = request.headers.get("content-type", "").lower()
                    if "application/json" in content_type:
                        try:
                            # Parse the JSON to validate it
                            body_json = json.loads(body_bytes.decode('utf-8'))

                            # Sanitize the JSON data
                            sanitized_data = sanitize_input(body_json)

                            # Replace the request body with sanitized data
                            request._body = json.dumps(sanitized_data).encode('utf-8')

                        except json.JSONDecodeError:
                            raise HTTPException(
                                status_code=400,
                                detail="Invalid JSON in request body"
                            )
                        except UnicodeDecodeError:
                            raise HTTPException(
                                status_code=400,
                                detail="Invalid character encoding in request body"
                            )

            except Exception as e:
                if isinstance(e, HTTPException):
                    raise
                else:
                    raise HTTPException(
                        status_code=400,
                        detail="Error reading request body"
                    )

        # Continue with the request
        response = await call_next(request)
        return response

    async def set_body(self, request: Request, body: bytes):
        """Helper method to set request body."""
        async def receive():
            return {"type": "http.request", "body": body}

        request._receive = receive


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """
    Enhanced middleware for input validation and sanitization.
    """

    def __init__(
        self,
        app,
        max_body_size: int = 1024 * 1024,  # 1MB
        allowed_content_types: Optional[list] = None,
        validate_query_params: bool = True,
        validate_headers: bool = True
    ):
        super().__init__(app)
        self.max_body_size = max_body_size
        self.allowed_content_types = allowed_content_types or [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "text/plain"
        ]
        self.validate_query_params = validate_query_params
        self.validate_headers = validate_headers

    async def dispatch(self, request: Request, call_next):
        # Validate content type
        content_type = request.headers.get("content-type", "")
        if content_type and not any(ct in content_type.lower() for ct in self.allowed_content_types):
            raise HTTPException(
                status_code=400,
                detail=f"Content type not allowed: {content_type}. Allowed types: {', '.join(self.allowed_content_types)}"
            )

        # Validate and sanitize query parameters
        if self.validate_query_params:
            for key, value in request.query_params.items():
                # Check for potentially dangerous patterns
                if self._has_dangerous_pattern(value):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Dangerous pattern detected in query parameter '{key}'"
                    )

                # Sanitize the value
                sanitized_value = clean_user_input(value)
                # Note: We can't modify query params in the request object directly
                # The validation happens during parameter parsing by Pydantic models

        # Validate and sanitize headers if needed
        if self.validate_headers:
            for key, value in request.headers.items():
                if self._has_dangerous_pattern(value):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Dangerous pattern detected in header '{key}'"
                    )

        # Get and validate the request body
        if request.method in ["POST", "PUT", "PATCH"]:
            body_bytes = await request.body()

            if body_bytes and len(body_bytes) > 0:
                # Check size
                if len(body_bytes) > self.max_body_size:
                    raise HTTPException(
                        status_code=413,
                        detail="Request body too large"
                    )

                # Process based on content type
                content_type = request.headers.get("content-type", "").lower()

                if "application/json" in content_type:
                    try:
                        body_json = json.loads(body_bytes.decode('utf-8'))

                        # Sanitize the JSON data
                        sanitized_data = self._deep_sanitize(body_json)

                        # Replace the request body
                        request._body = json.dumps(sanitized_data).encode('utf-8')

                    except json.JSONDecodeError:
                        raise HTTPException(
                            status_code=400,
                            detail="Invalid JSON in request body"
                        )
                    except UnicodeDecodeError:
                        raise HTTPException(
                            status_code=400,
                            detail="Invalid character encoding in request body"
                        )
                elif "text/" in content_type:
                    # For text content, sanitize the raw string
                    try:
                        text_content = body_bytes.decode('utf-8')
                        sanitized_text = clean_user_input(text_content)
                        request._body = sanitized_text.encode('utf-8')
                    except UnicodeDecodeError:
                        raise HTTPException(
                            status_code=400,
                            detail="Invalid character encoding in request body"
                        )

        # Continue with the request
        response = await call_next(request)
        return response

    def _has_dangerous_pattern(self, value: str) -> bool:
        """Check if a value contains dangerous patterns."""
        if not isinstance(value, str):
            return False

        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',               # JavaScript protocol
            r'on\w+\s*=',                # Event handlers
            r'<iframe[^>]*>.*?</iframe>', # Iframe tags
            r'<object[^>]*>.*?</object>', # Object tags
            r'<embed[^>]*>.*?</embed>',   # Embed tags
            r'<link[^>]*>',               # Link tags
            r'<meta[^>]*>',               # Meta tags
            r'eval\s*\(',                 # eval function
            r'expression\s*\(',           # expression function
        ]

        value_lower = value.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, value_lower, re.IGNORECASE | re.DOTALL):
                return True

        return False

    def _deep_sanitize(self, obj: Any) -> Any:
        """Recursively sanitize an object."""
        if isinstance(obj, str):
            return clean_user_input(obj)
        elif isinstance(obj, dict):
            return {key: self._deep_sanitize(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_sanitize(item) for item in obj]
        else:
            return obj


def setup_validation_middleware(app, **kwargs):
    """
    Helper function to add input validation middleware to the application.

    Args:
        app: FastAPI application instance
        **kwargs: Additional arguments for the validation middleware
    """
    app.add_middleware(InputSanitizationMiddleware, **kwargs)