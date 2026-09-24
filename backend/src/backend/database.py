from __future__ import annotations

from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.config import settings

# PostgreSQL and SQLite (in-memory) database configuration

engine_options: dict[str, Any] = {"pool_pre_ping": True}
if settings.database_url.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}
    if ":memory:" in settings.database_url:
        engine_options["poolclass"] = StaticPool


# SQLAlchemy engine and session setup

engine = create_engine(settings.database_url, **engine_options)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


# DB initialization


def init_database() -> None:
    from backend.models.audit_log import AuditLog  # noqa: F401

    Base.metadata.create_all(bind=engine)
