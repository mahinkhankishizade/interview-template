from app.repositories.conversation_repository import ConversationRepository
from app.services.llm_service import LLMType


class ConversationNotFoundError(Exception):
    """Raised when a requested conversation does not exist."""


class ConversationEndedError(Exception):
    """Raised on an action that is not allowed once a conversation has ended
    (e.g. ending it again, or adding a query to it)."""


# Service = business logic. It orchestrates the repository, enforces rules
# that go beyond schema validation, and raises domain errors. Routes stay
# thin; repos stay dumb (just SQL).
#
# A conversation is "ended" once it has been rated: quality_metric is NULL
# while open and holds the rating once ended. That single fact drives both
# end_conversation (can't end twice) and QueryService (can't add queries to
# an ended conversation).


class ConversationService:
    def __init__(self, repo: ConversationRepository):
        self.repo = repo

    def list_conversations(self) -> list[dict]:
        return self.repo.get_all()

    def get_conversation(self, conversation_id: int) -> dict:
        conversation = self.repo.get_by_id(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(
                f"Conversation {conversation_id} not found"
            )
        return conversation

    def start_conversation(self, llm_type: LLMType = LLMType.A) -> dict:
        """Start a new conversation using the chosen LLM and return it
        (quality_metric is NULL until it is ended)."""
        return self.repo.create(llm_model=llm_type.value)

    def end_conversation(self, conversation_id: int, quality_metric: bool) -> dict:
        """Rate a conversation and close it. Raises if it does not exist or
        has already ended."""
        conversation = self.repo.get_by_id(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(
                f"Conversation {conversation_id} not found"
            )
        if conversation["quality_metric"] is not None:
            raise ConversationEndedError(
                f"Conversation {conversation_id} has already ended"
            )
        return self.repo.set_quality_metric(conversation_id, quality_metric)
