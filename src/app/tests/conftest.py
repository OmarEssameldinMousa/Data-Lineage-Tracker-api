import pytest_asyncio
import pytest
from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from app.core.dependencies import get_db
from app.core.settings import get_settings
from app.models import Base
from app.main import app

settings = get_settings()

engine = create_async_engine(settings.TEST_DATABASE_URL, future=True)
TestingSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)

# ----------------------------
# DB SETUP / TEARDOWN
# ----------------------------

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ----------------------------
# OVERRIDE DB DEPENDENCY
# ----------------------------

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


# ----------------------------
# HTTP CLIENT
# ----------------------------

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:
        yield client