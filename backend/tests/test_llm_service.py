"""Unit tests for the mock LLM services. No database, no HTTP: they are pure
functions of the input query, so these just pin down the canned responses and
the shared interface."""

from app.services.llm_service import (
    LLMService,
    LLMServiceA,
    LLMServiceB,
    llm_a,
    llm_b,
)


def test_llm_a_responds_with_checking_message():
    assert llm_a.respond("anything") == "hi, we are checking your query"


def test_llm_b_responds_with_fullname_prompt():
    assert llm_b.respond("anything") == "hi, please provide your fullname"


def test_response_is_independent_of_the_query():
    assert llm_a.respond("") == llm_a.respond("a totally different query")
    assert llm_b.respond("") == llm_b.respond("a totally different query")


def test_both_share_the_llm_service_interface():
    assert isinstance(llm_a, LLMService)
    assert isinstance(llm_b, LLMService)
    assert isinstance(LLMServiceA(), LLMService)
    assert isinstance(LLMServiceB(), LLMService)
