"""Tests for the /users routes. The service dependency is overridden with one
backed by the in-memory fake repository, so these run with no database and
focus on HTTP concerns: status codes, response shapes, and validation."""

import pytest
from fastapi.testclient import TestClient

from app.deps import get_user_service
from app.main import app
from app.services.user_service import UserService
from tests.conftest import FakeUserRepository


@pytest.fixture
def client():
    # One fake repo per test so state (created users) persists across the
    # requests within that test, but not between tests.
    repo = FakeUserRepository()
    app.dependency_overrides[get_user_service] = lambda: UserService(repo)
    # Not using TestClient as a context manager -> app lifespan (which opens
    # the real DB pool) does not run, so no database is touched.
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_user_returns_201(client):
    resp = client.post(
        "/users", json={"email": "ada@example.com", "full_name": "Ada Lovelace"}
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == 1
    assert body["email"] == "ada@example.com"


def test_list_users_returns_created_users(client):
    client.post("/users", json={"email": "a@example.com", "full_name": "Alice"})
    client.post("/users", json={"email": "b@example.com", "full_name": "Bob"})

    resp = client.get("/users")

    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_user_returns_200(client):
    client.post("/users", json={"email": "ada@example.com", "full_name": "Ada"})

    resp = client.get("/users/1")

    assert resp.status_code == 200
    assert resp.json()["email"] == "ada@example.com"


def test_get_missing_user_returns_404(client):
    resp = client.get("/users/999")

    assert resp.status_code == 404


def test_create_duplicate_email_returns_409(client):
    payload = {"email": "ada@example.com", "full_name": "Ada"}
    client.post("/users", json=payload)

    resp = client.post("/users", json=payload)

    assert resp.status_code == 409


def test_create_invalid_email_returns_422(client):
    resp = client.post("/users", json={"email": "not-an-email", "full_name": "X"})

    assert resp.status_code == 422
