from datetime import datetime

from pydantic import BaseModel

from app.services.llm_service import LLMType


class ConversationStart(BaseModel):
    """Request body for starting a conversation: pick which LLM it will use
    (defaults to A). The choice is fixed for the life of the conversation."""

    llm_type: LLMType = LLMType.A


class ConversationEnd(BaseModel):
    """Request body for ending (rating) a conversation."""

    quality_metric: bool


class Conversation(BaseModel):
    """Response shape for a conversation.

    quality_metric is NULL while the conversation is open, and set to the
    rating once it has ended, so it is optional. llm_model records which mock
    LLM the conversation is using (defaults to A).
    """

    id: int
    quality_metric: bool | None = None
    created_at: datetime
    llm_model: LLMType = LLMType.A
