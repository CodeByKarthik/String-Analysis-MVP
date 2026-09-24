import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from backend.api.app import app


@pytest.fixture(scope="session")
def client() -> Generator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
