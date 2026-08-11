import pytest
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_session

# In-memory SQLite database, shared across a single connection for the whole test run
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def get_test_session():
    with Session(test_engine) as session:
        yield session


# Override the app's real database dependency with the test one
app.dependency_overrides[get_session] = get_test_session


@pytest.fixture
def session():
    """Create a clean database schema before each test, drop it after."""
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)