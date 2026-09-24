from __future__ import annotations

import json
import uuid
from typing import Any
from urllib.parse import parse_qs

from fastapi import Request
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from backend.utils.audit import AuditEntry, save_audit_log
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def _decode_body(body: bytes) -> Any | None:
    """
    Decode a JSON-encoded request or response body.

    Args:
        body (bytes): The request or response body as bytes.

    Returns:
        Any | None: The decoded JSON object, or the raw text
        if decoding fails, or None if the body is empty.
    """
    if not body:
        return None
    text = body.decode("utf-8", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _parse_query_parameters(query_string: bytes) -> dict[str, list[str]]:
    """
    Parse query parameters from a URL-encoded query string.

    Args:
        query_string (bytes): The URL-encoded query string as bytes.

    Returns:
        dict[str, list[str]]: A dictionary mapping query parameter
        names to lists of values.
    """
    return parse_qs(query_string.decode(), keep_blank_values=True)


class AuditLoggingMiddleware:
    """
    Middleware for logging audit information for each
    HTTP request and response.
    """

    def __init__(self, app: ASGIApp) -> None:
        """
        Initialize the AuditLoggingMiddleware with the given ASGI app.

        Args:
            app (ASGIApp): The ASGI application instance.
        """
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Handle an incoming HTTP request, capturing audit information.

        Args:
            scope (Scope): The ASGI scope for the request.
            receive (Receive): The ASGI receive callable.
            send (Send): The ASGI send callable.
        """
        if scope["type"] != "http" or scope["path"] == "/metrics":
            await self.app(scope, receive, send)
            return

        request_body = bytearray()
        response_body = bytearray()
        status_code = 500

        async def receive_with_capture() -> Message:
            """
            Capture the incoming HTTP request body.

            Returns:
                Message: The ASGI message received.
            """
            message = await receive()
            if message["type"] == "http.request":
                request_body.extend(message.get("body", b""))
            return message

        async def send_with_capture(message: Message) -> None:
            """
            Capture the response body and status code.

            Args:
                message (Message): The ASGI message to be sent.
            """
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            elif message["type"] == "http.response.body":
                response_body.extend(message.get("body", b""))
            await send(message)

        try:
            await self.app(scope, receive_with_capture, send_with_capture)
        finally:
            client = scope.get("client")
            entry = AuditEntry(
                request_id=scope["state"]["request_id"],
                method=scope["method"],
                path=scope["path"],
                query_parameters=_parse_query_parameters(
                    scope.get("query_string", b"")
                ),
                request_body=_decode_body(bytes(request_body)),
                response_body=_decode_body(bytes(response_body)),
                status_code=status_code,
                client_ip=client[0] if client else None,
            )
            await run_in_threadpool(save_audit_log, entry)


class RequestResponseLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    """

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        """
        Log the incoming request and outgoing response metadata.

        Args:
            request (Request): The incoming FastAPI request object.
            call_next (Any): The next middleware or route handler to call.

        Returns:
            Any: The response object returned by the next middleware or
            route handler.
        """
        if request.url.path == "/metrics":
            return await call_next(request)

        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        logger.info(
            "request_received",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            query_params=_parse_query_parameters(
                request.scope.get("query_string", b"")
            ),
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
