import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to sys.path
TESTS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TESTS_DIR.parent
BACKEND_DIR = PROJECT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.main import app
from app.database.session import Base, get_db
from app.database.init_db import seed_sample_defects_if_empty
from app.models.user import User
from app.utils.security import get_password_hash, create_access_token

# Test SQLite in-memory or dedicated test database
TEST_DB_PATH = PROJECT_DIR / "test_bug_platform.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    seed_sample_defects_if_empty(db)
    db.close()
    yield
    # Teardown
    Base.metadata.drop_all(bind=test_engine)
    if TEST_DB_PATH.exists():
        try:
            TEST_DB_PATH.unlink()
        except Exception:
            pass

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    user = db_session.query(User).filter(User.email == "dev_tester@example.com").first()
    if not user:
        user = User(
            name="Test Developer",
            email="dev_tester@example.com",
            password_hash=get_password_hash("password123")
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    token = create_access_token(data={"sub": test_user.id, "email": test_user.email})
    return {"Authorization": f"Bearer {token}"}
