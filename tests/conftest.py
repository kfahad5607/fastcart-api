import os
import subprocess
import asyncio
from typing import AsyncIterator, Generator
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from main import app
from db.sql import get_session

TEST_DB_URL = "postgresql+asyncpg://testuser:testpass@localhost:5433/test_db"
engine = create_async_engine(TEST_DB_URL, echo=True)
async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop(request) -> Generator:  # noqa: indirect usage
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Runs the setup script to start test DB & apply migrations."""
    os.environ["TESTING"] = "1"
    subprocess.run(["./scripts/setup_test_db.sh"], check=True)

    yield  # Run tests

    subprocess.run(["./scripts/teardown_test_db.sh"], check=True)

@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session

async def get_test_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session

@pytest_asyncio.fixture(scope="function")
async def client():
    app.dependency_overrides[get_session] = get_test_session
    """Provides a test client for FastAPI."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test/api/v1/") as ac:
        yield ac
    app.dependency_overrides.clear()
