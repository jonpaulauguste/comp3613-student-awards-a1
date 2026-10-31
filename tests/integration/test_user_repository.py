"""Integration tests: UserRepository with a real (in-memory) database."""

import pytest

from app.repositories.user import UserRepository
from app.schemas.user import RegularUserCreate
from tests.conftest import make_user


def test_create_user(db):
    repo = UserRepository(db)
    new_user = RegularUserCreate(username="carl", email="carl@example.com", password="hashed")

    created = repo.create(new_user)

    assert created.id is not None
    assert created.username == "carl"
    assert created.role == "regular_user"
    assert created.total_points == 0


def test_get_user_by_username(db):
    user = make_user(db, "bob")
    found = UserRepository(db).get_by_username("bob")
    assert found.id == user.id


def test_get_user_by_email(db):
    user = make_user(db, "bob")
    found = UserRepository(db).get_by_email("bob@example.com")
    assert found.id == user.id


def test_get_unknown_user(db):
    assert UserRepository(db).get_by_username("ghost") is None


def test_add_points(db):
    user = make_user(db, points=10)
    updated = UserRepository(db).add_points(user.id, 5)
    assert updated.total_points == 15


def test_deduct_points(db):
    user = make_user(db, points=10)
    updated = UserRepository(db).deduct_points(user.id, 4)
    assert updated.total_points == 6


def test_deduct_too_many_points(db):
    user = make_user(db, points=4)
    with pytest.raises(ValueError):
        UserRepository(db).deduct_points(user.id, 5)
    db.refresh(user)
    assert user.total_points == 4


def test_points_must_be_positive(db):
    user = make_user(db, points=10)
    repo = UserRepository(db)
    with pytest.raises(ValueError):
        repo.add_points(user.id, 0)
    with pytest.raises(ValueError):
        repo.deduct_points(user.id, -3)


def test_add_points_unknown_user(db):
    with pytest.raises(ValueError):
        UserRepository(db).add_points(12345, 1)


def test_add_points_without_commit(db):
    user = make_user(db, points=10)
    UserRepository(db).add_points(user.id, 5, commit=False)
    db.rollback()
    db.refresh(user)
    assert user.total_points == 10
