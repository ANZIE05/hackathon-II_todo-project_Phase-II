from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import uuid
import time


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to generate and attach a unique request ID to each request for traceability.
    """

    async def dispatch(self, request: Request, call_next):
        # Generate a unique request ID
        request_id = str(uuid.uuid4())

        # Add the request ID to the request state
        request.state.request_id = request_id

        # Add the request ID to the response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log request information with request ID for traceability.
    """

    async def dispatch(self, request: Request, call_next):
        # Generate a unique request ID if not already present
        request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        # Add timing information to response headers
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        response.headers["X-Request-ID"] = request_id

        # Log request info (in a real app, you'd use proper logging)
        print(f"REQUEST_ID={request_id} "
              f"METHOD={request.method} "
              f"PATH={request.url.path} "
              f"STATUS={response.status_code} "
              f"TIME={process_time:.4f}s")

        return response