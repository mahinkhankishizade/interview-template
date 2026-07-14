"""Integration tests for QueryRepository. These hit a real Postgres database
(the throwaway `borderless_test` DB) to prove the SQL actually works."""

from app.repositories.conversation_repository import ConversationRepository
from app.repositories.query_repository import QueryRepository


def _make_conversation(db_conn) -> int:
    return ConversationRepository(db_conn).create()["id"]


def test_create_returns_the_new_row(db_conn):
    conv_id = _make_conversation(db_conn)
    repo = QueryRepository(db_conn)

    query = repo.create(
        query_text="What is your name?", conversation_id=conv_id, is_input=True
    )

    assert query["id"] == 1
    assert query["query_text"] == "What is your name?"
    assert query["is_input"] is True
    assert query["conversation_id"] == conv_id
    assert query["created_at"] is not None


def test_get_by_id_returns_the_row(db_conn):
    conv_id = _make_conversation(db_conn)
    repo = QueryRepository(db_conn)
    created = repo.create(
        query_text="hi", conversation_id=conv_id, is_input=True
    )

    fetched = repo.get_by_id(created["id"])

    assert fetched == created


def test_get_by_id_returns_none_when_missing(db_conn):
    repo = QueryRepository(db_conn)

    assert repo.get_by_id(999) is None


def test_get_by_conversation_returns_only_matching_rows(db_conn):
    conv_a = _make_conversation(db_conn)
    conv_b = _make_conversation(db_conn)
    repo = QueryRepository(db_conn)
    repo.create(query_text="a1", conversation_id=conv_a, is_input=True)
    repo.create(query_text="a2", conversation_id=conv_a, is_input=False)
    repo.create(query_text="b1", conversation_id=conv_b, is_input=True)

    rows = repo.get_by_conversation(conv_a)

    assert [r["query_text"] for r in rows] == ["a1", "a2"]


def test_get_all_returns_rows_ordered_by_id(db_conn):
    conv_id = _make_conversation(db_conn)
    repo = QueryRepository(db_conn)
    repo.create(query_text="first", conversation_id=conv_id, is_input=True)
    repo.create(query_text="second", conversation_id=conv_id, is_input=False)

    rows = repo.get_all()

    assert [r["query_text"] for r in rows] == ["first", "second"]


def test_deleting_conversation_cascades_to_queries(db_conn):
    conv_id = _make_conversation(db_conn)
    repo = QueryRepository(db_conn)
    repo.create(query_text="hi", conversation_id=conv_id, is_input=True)

    db_conn.execute("DELETE FROM conversations WHERE id = %s", (conv_id,))
    db_conn.commit()

    assert repo.get_all() == []
