"""Tests for the /queries routes. The service dependencies are overridden with
ones backed by in-memory fake repositories, so these run with no database and
focus on HTTP concerns: status codes, response shapes, and validation."""

import pytest
from fastapi.testclient import TestClient

from app.deps import get_conversation_service, get_query_service
from app.main import app
from app.services.conversation_service import ConversationService
from app.services.query_service import QueryService
from tests.conftest import FakeConversationRepository, FakeQueryRepository


@pytest.fixture
def client():
    conv_repo = FakeConversationRepository()
    query_repo = FakeQueryRepository()
    app.dependency_overrides[get_conversation_service] = (
        lambda: ConversationService(conv_repo)
    )
    app.dependency_overrides[get_query_service] = lambda: QueryService(
        query_repo, conv_repo
    )
    yield TestClient(app)
    app.dependency_overrides.clear()


def _create_conversation(client) -> int:
    return client.post("/conversations/start").json()["id"]


def test_input_query_returns_input_and_generated_output(client):
    # conversation defaults to LLM A
    conv_id = _create_conversation(client)

    resp = client.post(
        "/queries", json={"query_text": "hello", "conversation_id": conv_id}
    )

    assert resp.status_code == 201
    turns = resp.json()
    assert len(turns) == 2
    inp, out = turns
    assert inp["query_text"] == "hello"
    assert inp["is_input"] is True
    assert inp["conversation_id"] == conv_id
    # LLM A's canned reply, stored as the output turn
    assert out["query_text"] == "hi, we are checking your query"
    assert out["is_input"] is False


def test_output_uses_the_conversations_llm(client):
    # conversation started on LLM B -> generated output comes from B
    conv_id = client.post(
        "/conversations/start", json={"llm_type": "B"}
    ).json()["id"]

    resp = client.post(
        "/queries", json={"query_text": "hi", "conversation_id": conv_id}
    )

    assert resp.status_code == 201
    assert resp.json()[1]["query_text"] == "hi, please provide your fullname"


def test_agent_output_stored_without_generating_a_reply(client):
    conv_id = _create_conversation(client)

    resp = client.post(
        "/queries",
        json={
            "query_text": "agent interjects",
            "conversation_id": conv_id,
            "is_input": False,
        },
    )

    assert resp.status_code == 201
    turns = resp.json()
    assert len(turns) == 1
    assert turns[0]["is_input"] is False
    assert turns[0]["query_text"] == "agent interjects"


def test_create_query_for_missing_conversation_returns_404(client):
    resp = client.post(
        "/queries", json={"query_text": "hi", "conversation_id": 999}
    )

    assert resp.status_code == 404


def test_create_query_on_ended_conversation_returns_409(client):
    conv_id = _create_conversation(client)
    client.post(f"/conversations/{conv_id}/end", json={"quality_metric": True})

    resp = client.post(
        "/queries", json={"query_text": "too late", "conversation_id": conv_id}
    )

    assert resp.status_code == 409
    assert "ended" in resp.json()["detail"]


def test_create_query_missing_text_returns_422(client):
    conv_id = _create_conversation(client)

    resp = client.post("/queries", json={"conversation_id": conv_id})

    assert resp.status_code == 422


def test_list_queries_returns_input_and_output_per_submission(client):
    conv_id = _create_conversation(client)
    client.post("/queries", json={"query_text": "a", "conversation_id": conv_id})

    resp = client.get("/queries")

    assert resp.status_code == 200
    # one input submission stores two turns
    assert len(resp.json()) == 2


def test_get_query_returns_200(client):
    conv_id = _create_conversation(client)
    client.post("/queries", json={"query_text": "hi", "conversation_id": conv_id})

    resp = client.get("/queries/1")

    assert resp.status_code == 200
    assert resp.json()["query_text"] == "hi"


def test_get_missing_query_returns_404(client):
    resp = client.get("/queries/999")

    assert resp.status_code == 404
