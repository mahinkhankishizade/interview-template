"""Unit tests for UserService. No database: the service is given an in-memory
fake repository, so these tests exercise business rules in isolation."""

import pytest

from app.models.user import UserCreate
from app.services.user_service import (
    UserAlreadyExistsError,
    UserNotFoundError,
    UserService,
)


def test_create_user_returns_created_user(fake_repo):
    service = UserService(fake_repo)

    user = service.create_user(UserCreate(email="ada@example.com", full_name="Ada"))

    assert user["id"] == 1
    assert user["email"] == "ada@example.com"


def test_create_user_rejects_duplicate_email(fake_repo):
    service = UserService(fake_repo)
    service.create_user(UserCreate(email="ada@example.com", full_name="Ada"))

    with pytest.raises(UserAlreadyExistsError):
        service.create_user(UserCreate(email="ada@example.com", full_name="Someone"))


def test_get_user_returns_existing_user(fake_repo):
    service = UserService(fake_repo)
    created = service.create_user(UserCreate(email="ada@example.com", full_name="Ada"))

    assert service.get_user(created["id"]) == created


def test_get_user_raises_when_missing(fake_repo):
    service = UserService(fake_repo)

    with pytest.raises(UserNotFoundError):
        service.get_user(999)


def test_list_users_returns_all(fake_repo):
    service = UserService(fake_repo)
    service.create_user(UserCreate(email="a@example.com", full_name="Alice"))
    service.create_user(UserCreate(email="b@example.com", full_name="Bob"))

    users = service.list_users()

    assert len(users) == 2
