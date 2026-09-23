from __future__ import annotations

import uuid
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class RequestResponseLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging incoming requests and
    outgoing response metadata.
    """

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        """
        Log the incoming request and outgoing response metadata.

        Args:
            request (Request): The incoming FastAPI request object.
            call_next (Any): The next middleware or route handler to call.

        Returns:
            Any: The response object returned by the next middleware or route handler.
        """

        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        logger.info(
            "request_received",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
        )

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request_completed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
        )
        return response
