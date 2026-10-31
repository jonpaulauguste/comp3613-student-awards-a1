"""Shared test setup.

Unit tests mock everything (no database).
Integration tests use a fresh in-memory SQLite database for every test.
"""

import os

# These must be set before the app is imported.
os.environ["ENV"] = "pytest"
os.environ["SECRET_KEY"] = "pytest-secret-key-that-is-long-enough-for-hs256"
os.environ["DATABASE_URI"] = "sqlite:///./.pytest_unused.db"  # never used

from datetime import date, timedelta  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402

import app.models  # noqa: E402,F401
from app.database import get_session  # noqa: E402
from app.main import app  # noqa: E402
from app.models.award import Award  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.volunteer_session import VolunteerSession  # noqa: E402
from app.utilities.security import create_access_token, encrypt_password  # noqa: E402


@pytest.fixture
def engine():
    """A new empty in-memory database for each test."""
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)
    yield test_engine
    test_engine.dispose()


@pytest.fixture
def db(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture
def client(engine):
    """A test client whose app uses the in-memory database."""

    def use_test_database():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = use_test_database
    yield TestClient(app)
    app.dependency_overrides.clear()


# ---- helper functions that put test data in the database ----

def make_user(db, username="bob", role="regular_user", points=0, password="bobpass"):
    user = User(
        username=username,
        email=username + "@example.com",
        password=encrypt_password(password),
        role=role,
        total_points=points,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_award(db, name="Coffee Voucher", points_required=15, stock_quantity=5):
    award = Award(
        name=name,
        description="Description of " + name,
        points_required=points_required,
        stock_quantity=stock_quantity,
    )
    db.add(award)
    db.commit()
    db.refresh(award)
    return award


def make_session(db, student, hours=3.0, status="pending", description="Beach Cleanup"):
    row = VolunteerSession(
        student_id=student.id,
        description=description,
        hours_logged=hours,
        date=date.today() - timedelta(days=1),
        status=status,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def auth_header(user):
    """Authorization header with a valid token for this user."""
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"Authorization": "Bearer " + token}


@pytest.fixture
def student(db):
    return make_user(db, "bob", "regular_user")


@pytest.fixture
def admin(db):
    return make_user(db, "admin", "admin", password="adminpass")
