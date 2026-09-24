from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class AuditLog(Base):
    """
    Represents an audit log entry for tracking API requests and responses.

    Attributes:
        id (int): The primary key of the audit log entry.
        request_id (str): The unique identifier for the request.
        method (str): The HTTP method of the request.
        path (str): The path of the request.
        query_parameters (Any | None): The query parameters of the request.
        request_body (Any | None): The body of the request.
        response_body (Any | None): The body of the response.
        status_code (int): The HTTP status code of the response.
        client_ip (str | None): The IP address of the client making the request.
        created_at (datetime): The timestamp when the audit log entry was created.
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[str] = mapped_column(String(36), index=True)
    method: Mapped[str] = mapped_column(String(10))
    path: Mapped[str] = mapped_column(String(255), index=True)
    query_parameters: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    request_body: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    response_body: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    status_code: Mapped[int] = mapped_column(Integer, index=True)
    client_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
