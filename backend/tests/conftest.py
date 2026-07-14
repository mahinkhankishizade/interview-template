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
    conn.execute("TRUNCATE users, conversations, query RESTART IDENTITY CASCADE")
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


class FakeConversationRepository:
    """In-memory stand-in for ConversationRepository, matching its interface."""

    def __init__(self):
        self._rows: list[dict] = []
        self._next_id = 1

    def get_all(self) -> list[dict]:
        return list(self._rows)

    def get_by_id(self, conversation_id: int) -> dict | None:
        return next((r for r in self._rows if r["id"] == conversation_id), None)

    def create(self, llm_model: str = "A") -> dict:
        row = {
            "id": self._next_id,
            "quality_metric": None,
            "created_at": datetime.now(timezone.utc),
            "llm_model": llm_model,
        }
        self._rows.append(row)
        self._next_id += 1
        return row

    def set_quality_metric(
        self, conversation_id: int, quality_metric: bool
    ) -> dict | None:
        row = self.get_by_id(conversation_id)
        if row is None:
            return None
        row["quality_metric"] = quality_metric
        return row


class FakeQueryRepository:
    """In-memory stand-in for QueryRepository, matching its interface."""

    def __init__(self):
        self._rows: list[dict] = []
        self._next_id = 1

    def get_all(self) -> list[dict]:
        return list(self._rows)

    def get_by_id(self, query_id: int) -> dict | None:
        return next((r for r in self._rows if r["id"] == query_id), None)

    def get_by_conversation(self, conversation_id: int) -> list[dict]:
        return [r for r in self._rows if r["conversation_id"] == conversation_id]

    def create(
        self, query_text: str, conversation_id: int, is_input: bool
    ) -> dict:
        row = {
            "id": self._next_id,
            "query_text": query_text,
            "is_input": is_input,
            "created_at": datetime.now(timezone.utc),
            "conversation_id": conversation_id,
        }
        self._rows.append(row)
        self._next_id += 1
        return row


@pytest.fixture
def fake_conversation_repo() -> FakeConversationRepository:
    return FakeConversationRepository()


@pytest.fixture
def fake_query_repo() -> FakeQueryRepository:
    return FakeQueryRepository()
