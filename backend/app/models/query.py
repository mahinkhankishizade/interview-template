from datetime import datetime

from pydantic import BaseModel


class QueryCreate(BaseModel):
    """Request body for submitting a query to a conversation.

    is_input marks the turn: True for a user input (the service will auto-
    generate the LLM's output turn using the conversation's chosen model),
    False for an agent output submitted directly (stored as-is, no
    generation). Which LLM answers is fixed on the conversation, not here.
    """

    query_text: str
    conversation_id: int
    is_input: bool = True


class Query(BaseModel):
    """Response shape for a query (one turn: input or output)."""

    id: int
    query_text: str
    is_input: bool
    created_at: datetime
    conversation_id: int
