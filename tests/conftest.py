"""
Shared test fixtures for HiveNet.

Pytest auto-loads this file — no imports needed in test files.
Any fixture defined here is available to every test in tests/ and subfolders.
"""
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models import Base, User
from app.database import get_db
from app.auth import hash_password, create_token


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    TestSession = async_sessionmaker(test_engine, expire_on_commit=False)
    async with TestSession() as session:
        yield session


@pytest.fixture
def client(test_engine):
    TestSession = async_sessionmaker(test_engine, expire_on_commit=False)

    async def override_get_db():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_user(db_session):
    user = User(
        username="sampleuser",
        email_address="sample@test.com",
        hashed_password=hash_password("password123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(sample_user):
    token = create_token(sample_user.id)
    return {"Authorization": f"Bearer {token}"}
