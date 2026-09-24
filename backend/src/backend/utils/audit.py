from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from backend.database import SessionLocal
from backend.models.audit_log import AuditLog
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class AuditEntry:
    request_id: str
    method: str
    path: str
    query_parameters: dict[str, list[str]]
    request_body: Any | None
    response_body: Any | None
    status_code: int
    client_ip: str | None


def save_audit_log(entry: AuditEntry) -> None:
    with SessionLocal() as session:
        try:
            session.add(AuditLog(**asdict(entry)))
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            logger.exception(
                "audit_log_persistence_failed",
                request_id=entry.request_id,
                path=entry.path,
            )
