"""Integration tests for ConversationRepository. These hit a real Postgres
database (the throwaway `borderless_test` DB) to prove the SQL actually works."""

from app.repositories.conversation_repository import ConversationRepository


def test_create_returns_the_new_row(db_conn):
    repo = ConversationRepository(db_conn)

    conv = repo.create()

    assert conv["id"] == 1
    assert conv["created_at"] is not None


def test_create_leaves_quality_metric_null(db_conn):
    repo = ConversationRepository(db_conn)

    conv = repo.create()

    assert conv["quality_metric"] is None


def test_create_defaults_llm_model_to_a(db_conn):
    repo = ConversationRepository(db_conn)

    conv = repo.create()

    assert conv["llm_model"] == "A"


def test_create_stores_the_chosen_llm_model(db_conn):
    repo = ConversationRepository(db_conn)

    conv = repo.create(llm_model="B")

    assert conv["llm_model"] == "B"
    assert repo.get_by_id(conv["id"])["llm_model"] == "B"


def test_get_by_id_returns_the_row(db_conn):
    repo = ConversationRepository(db_conn)
    created = repo.create()

    fetched = repo.get_by_id(created["id"])

    assert fetched == created


def test_get_by_id_returns_none_when_missing(db_conn):
    repo = ConversationRepository(db_conn)

    assert repo.get_by_id(999) is None


def test_get_all_returns_rows_ordered_by_id(db_conn):
    repo = ConversationRepository(db_conn)
    repo.create()
    repo.create()

    convs = repo.get_all()

    assert [c["id"] for c in convs] == [1, 2]


def test_get_all_is_empty_initially(db_conn):
    repo = ConversationRepository(db_conn)

    assert repo.get_all() == []


def test_set_quality_metric_updates_the_row(db_conn):
    repo = ConversationRepository(db_conn)
    created = repo.create()

    updated = repo.set_quality_metric(created["id"], True)

    assert updated["id"] == created["id"]
    assert updated["quality_metric"] is True
    assert repo.get_by_id(created["id"])["quality_metric"] is True


def test_set_quality_metric_returns_none_when_missing(db_conn):
    repo = ConversationRepository(db_conn)

    assert repo.set_quality_metric(999, True) is None
