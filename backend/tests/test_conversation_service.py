"""Unit tests for ConversationService. No database: the service is given an
in-memory fake repository, so these exercise business rules in isolation."""

import pytest

from app.services.conversation_service import (
    ConversationEndedError,
    ConversationNotFoundError,
    ConversationService,
)
from app.services.llm_service import LLMType


def test_start_conversation_defaults_to_llm_a(fake_conversation_repo):
    service = ConversationService(fake_conversation_repo)

    conv = service.start_conversation()

    assert conv["id"] == 1
    assert conv["quality_metric"] is None
    assert conv["llm_model"] == "A"


def test_start_conversation_stores_chosen_llm(fake_conversation_repo):
    service = ConversationService(fake_conversation_repo)

    conv = service.start_conversation(LLMType.B)

    assert conv["llm_model"] == "B"


def test_get_conversation_returns_existing(fake_conversation_repo):
    service = ConversationService(fake_conversation_repo)
    created = service.start_conversation()

    assert service.get_conversation(created["id"]) == created


def test_get_conversation_raises_when_missing(fake_conversation_repo):
    service = ConversationService(fake_conversation_repo)

    with pytest.raises(ConversationNotFoundError):
        service.get_conversation(999)


def test_list_conversations_returns_all(fake_conversation_repo):
    service = ConversationService(fake_conversation_repo)
    service.start_conversation()
    service.start_conversation()

    assert len(service.list_conversations()) == 2


def test_end_conversation_sets_quality_metric(fake_conversation_repo):
    service = ConversationService(fake_conversation_repo)
    conv = service.start_conversation()

    ended = service.end_conversation(conv["id"], quality_metric=True)

    assert ended["quality_metric"] is True
    assert service.get_conversation(conv["id"])["quality_metric"] is True


def test_end_conversation_raises_when_missing(fake_conversation_repo):
    service = ConversationService(fake_conversation_repo)

    with pytest.raises(ConversationNotFoundError):
        service.end_conversation(999, quality_metric=True)


def test_end_conversation_rejects_already_ended(fake_conversation_repo):
    service = ConversationService(fake_conversation_repo)
    conv = service.start_conversation()
    service.end_conversation(conv["id"], quality_metric=True)

    with pytest.raises(ConversationEndedError):
        service.end_conversation(conv["id"], quality_metric=False)
