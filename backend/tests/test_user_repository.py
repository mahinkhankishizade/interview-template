"""Integration tests for UserRepository. These hit a real Postgres database
(the throwaway `borderless_test` DB) to prove the SQL actually works."""

from app.repositories.user_repository import UserRepository


def test_create_returns_the_new_row(db_conn):
    repo = UserRepository(db_conn)

    user = repo.create(email="ada@example.com", full_name="Ada Lovelace")

    assert user["id"] == 1
    assert user["email"] == "ada@example.com"
    assert user["full_name"] == "Ada Lovelace"
    assert user["created_at"] is not None


def test_get_by_id_returns_the_row(db_conn):
    repo = UserRepository(db_conn)
    created = repo.create(email="ada@example.com", full_name="Ada Lovelace")

    fetched = repo.get_by_id(created["id"])

    assert fetched == created


def test_get_by_id_returns_none_when_missing(db_conn):
    repo = UserRepository(db_conn)

    assert repo.get_by_id(999) is None


def test_get_by_email_finds_the_row(db_conn):
    repo = UserRepository(db_conn)
    repo.create(email="ada@example.com", full_name="Ada Lovelace")

    fetched = repo.get_by_email("ada@example.com")

    assert fetched is not None
    assert fetched["email"] == "ada@example.com"


def test_get_all_returns_rows_ordered_by_id(db_conn):
    repo = UserRepository(db_conn)
    repo.create(email="a@example.com", full_name="Alice")
    repo.create(email="b@example.com", full_name="Bob")

    users = repo.get_all()

    assert [u["email"] for u in users] == ["a@example.com", "b@example.com"]


def test_get_all_is_empty_initially(db_conn):
    repo = UserRepository(db_conn)

    assert repo.get_all() == []
