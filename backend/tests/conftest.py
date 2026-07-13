from datetime import datetime, timezone
from pathlib import Path

import psycopg
import pytest
from psycopg.rows import dict_row

# Tests run against a SEPARATE database so they never touch dev data.
ADMIN_URL = "postgresql://postgres:postgres@localhost:5432/postgres"
TEST_DB = "borderless_test"
TEST_DB_URL = f"postgresql://postgres:postgres@localhost:5432/{TEST_DB}"

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "app" / "schema.sql"


@pytest.fixture(scope="session", autouse=True)
def _setup_test_database():
    """Create the test database once per test session and apply the schema."""
    # CREATE DATABASE cannot run inside a transaction -> autocommit.
    admin = psycopg.connect(ADMIN_URL, autocommit=True)
    with admin.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (TEST_DB,))
        if cur.fetchone() is None:
            cur.execute(f"CREATE DATABASE {TEST_DB}")
    admin.close()

    schema = SCHEMA_PATH.read_text()
    conn = psycopg.connect(TEST_DB_URL)
    conn.execute(schema)
    conn.commit()
    conn.close()
    yield


@pytest.fixture
def db_conn():
    """A clean connection to the test DB. Truncates tables before each test."""
    conn = psycopg.connect(TEST_DB_URL, row_factory=dict_row)
    conn.execute("TRUNCATE users RESTART IDENTITY CASCADE")
    conn.commit()
    yield conn
    conn.close()


class FakeUserRepository:
    """In-memory stand-in for UserRepository, matching its interface.

    Lets the service and route layers be tested with no database.
    """

    def __init__(self):
        self._rows: list[dict] = []
        self._next_id = 1

    def get_all(self) -> list[dict]:
        return list(self._rows)

    def get_by_id(self, user_id: int) -> dict | None:
        return next((r for r in self._rows if r["id"] == user_id), None)

    def get_by_email(self, email: str) -> dict | None:
        return next((r for r in self._rows if r["email"] == email), None)

    def create(self, email: str, full_name: str) -> dict:
        row = {
            "id": self._next_id,
            "email": email,
            "full_name": full_name,
            "created_at": datetime.now(timezone.utc),
        }
        self._rows.append(row)
        self._next_id += 1
        return row


@pytest.fixture
def fake_repo() -> FakeUserRepository:
    return FakeUserRepository()
