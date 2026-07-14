"""Tests for the /conversations routes. The service dependencies are overridden
with ones backed by in-memory fake repositories, so these run with no database
and focus on HTTP concerns: status codes, response shapes, and validation."""

import pytest
from fastapi.testclient import TestClient

from app.deps import get_conversation_service, get_query_service
from app.main import app
from app.services.conversation_service import ConversationService
from app.services.query_service import QueryService
from tests.conftest import FakeConversationRepository, FakeQueryRepository


@pytest.fixture
def client():
    # Share one conversation repo across both services so a conversation
    # created via /conversations is visible when listing its queries.
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


def test_start_conversation_returns_201_with_id(client):
    resp = client.post("/conversations/start")

    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == 1
    assert body["quality_metric"] is None


def test_start_conversation_defaults_to_llm_a(client):
    # No JSON payload at all: starting a conversation uses the default LLM (A).
    resp = client.post("/conversations/start")

    assert resp.status_code == 201
    assert resp.json()["llm_model"] == "A"


def test_start_conversation_with_chosen_llm(client):
    resp = client.post("/conversations/start", json={"llm_type": "B"})

    assert resp.status_code == 201
    assert resp.json()["llm_model"] == "B"


def test_start_conversation_rejects_invalid_llm(client):
    resp = client.post("/conversations/start", json={"llm_type": "C"})

    assert resp.status_code == 422


def test_list_conversations_returns_created(client):
    client.post("/conversations/start")
    client.post("/conversations/start")

    resp = client.get("/conversations")

    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_conversation_returns_200(client):
    client.post("/conversations/start")

    resp = client.get("/conversations/1")

    assert resp.status_code == 200
    assert resp.json()["quality_metric"] is None


def test_get_missing_conversation_returns_404(client):
    resp = client.get("/conversations/999")

    assert resp.status_code == 404


def test_list_conversation_queries_returns_200(client):
    client.post("/conversations/start")
    client.post("/queries", json={"query_text": "hi", "conversation_id": 1})

    resp = client.get("/conversations/1/queries")

    assert resp.status_code == 200
    # the input turn plus the LLM's generated output turn
    assert [q["query_text"] for q in resp.json()] == [
        "hi",
        "hi, we are checking your query",
    ]


def test_list_queries_for_missing_conversation_returns_404(client):
    resp = client.get("/conversations/999/queries")

    assert resp.status_code == 404


def test_end_conversation_rates_and_returns_200(client):
    client.post("/conversations/start")

    resp = client.post("/conversations/1/end", json={"quality_metric": True})

    assert resp.status_code == 200
    assert resp.json()["quality_metric"] is True


def test_end_missing_conversation_returns_404(client):
    resp = client.post("/conversations/999/end", json={"quality_metric": True})

    assert resp.status_code == 404


def test_end_already_ended_conversation_returns_409(client):
    client.post("/conversations/start")
    client.post("/conversations/1/end", json={"quality_metric": True})

    resp = client.post("/conversations/1/end", json={"quality_metric": False})

    assert resp.status_code == 409


def test_end_conversation_requires_quality_metric(client):
    client.post("/conversations/start")

    resp = client.post("/conversations/1/end", json={})

    assert resp.status_code == 422
