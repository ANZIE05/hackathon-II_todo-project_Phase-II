from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging
from typing import Optional
import json


# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log incoming requests for monitoring and debugging.
    """

    def __init__(self, app, logger_name: Optional[str] = None):
        super().__init__(app)
        self.logger = logging.getLogger(logger_name or __name__)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request details
        request_details = {
            "method": request.method,
            "path": str(request.url),
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
            "client": request.client.host if request.client else None,
            "timestamp": time.time(),
            "request_id": getattr(request.state, 'request_id', 'unknown')
        }

        # Skip logging for health checks to avoid noise
        if request.url.path != "/health":
            self.logger.info(
                f"REQUEST_START | "
                f"req_id={request_details['request_id']} | "
                f"method={request_details['method']} | "
                f"path={request_details['path']} | "
                f"client={request_details['client']}"
            )

        try:
            response = await call_next(request)
        except Exception as e:
            # Calculate process time for failed requests
            process_time = time.time() - start_time

            self.logger.error(
                f"REQUEST_FAILED | "
                f"req_id={getattr(request.state, 'request_id', 'unknown')} | "
                f"method={request.method} | "
                f"path={str(request.url)} | "
                f"status=500 | "
                f"process_time={process_time:.4f}s | "
                f"error={str(e)}"
            )

            raise

        # Calculate process time
        process_time = time.time() - start_time

        # Add process time to response headers
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"

        # Skip logging for health checks to avoid noise
        if request.url.path != "/health":
            self.logger.info(
                f"REQUEST_END | "
                f"req_id={getattr(request.state, 'request_id', 'unknown')} | "
                f"method={request.method} | "
                f"path={str(request.url)} | "
                f"status={response.status_code} | "
                f"process_time={process_time:.4f}s"
            )

        return response


class DetailedRequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    More detailed request logging middleware with additional information.
    """

    def __init__(self, app, logger_name: Optional[str] = None, log_body: bool = False):
        super().__init__(app)
        self.logger = logging.getLogger(logger_name or __name__)
        self.log_body = log_body

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Get request ID
        request_id = getattr(request.state, 'request_id', 'unknown')

        # Prepare log data
        log_data = {
            "timestamp": time.time(),
            "request_id": request_id,
            "method": request.method,
            "path": str(request.url),
            "full_url": str(request.url),
            "client_host": request.client.host if request.client else None,
            "client_port": request.client.port if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "content_type": request.headers.get("content-type"),
            "accept_encoding": request.headers.get("accept-encoding"),
            "referer": request.headers.get("referer"),
        }

        # Optionally log request body (be careful with sensitive data)
        if self.log_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    # Only log if content is reasonable size and not binary
                    if len(body_bytes) < 1000 and body_bytes.decode('utf-8', errors='ignore').isprintable():
                        log_data["request_body"] = body_bytes.decode('utf-8')
            except Exception:
                pass  # Don't log body if there's an error

        # Log the request start
        if request.url.path != "/health":  # Skip health checks
            self.logger.info(f"Request started: {json.dumps(log_data)}")

        try:
            response = await call_next(request)
        except Exception as e:
            process_time = time.time() - start_time
            error_log = {
                **log_data,
                "status_code": 500,
                "process_time": f"{process_time:.4f}s",
                "error": str(e),
                "error_type": type(e).__name__
            }
            self.logger.error(f"Request failed: {json.dumps(error_log)}")
            raise

        process_time = time.time() - start_time

        # Add response information
        response_log = {
            **log_data,
            "status_code": response.status_code,
            "process_time": f"{process_time:.4f}s",
            "content_length": response.headers.get("content-length", "unknown"),
            "content_type": response.headers.get("content-type", "unknown")
        }

        # Add process time to response headers
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"

        # Log the request end
        if request.url.path != "/health":  # Skip health checks
            log_level = logging.INFO if response.status_code < 400 else logging.WARNING
            if response.status_code >= 500:
                log_level = logging.ERROR
            self.logger.log(log_level, f"Request completed: {json.dumps(response_log)}")

        return response


def setup_logging_middleware(app, detailed: bool = False, log_body: bool = False):
    """
    Helper function to set up request logging middleware.

    Args:
        app: FastAPI application
        detailed: Whether to use detailed logging
        log_body: Whether to log request bodies (use cautiously)
    """
    if detailed:
        app.add_middleware(DetailedRequestLoggerMiddleware, log_body=log_body)
    else:
        app.add_middleware(RequestLoggerMiddleware)