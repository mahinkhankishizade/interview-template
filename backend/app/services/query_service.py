from app.models.query import QueryCreate
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.query_repository import QueryRepository
from app.services.conversation_service import (
    ConversationEndedError,
    ConversationNotFoundError,
)
from app.services.llm_service import LLMType, get_llm


class QueryNotFoundError(Exception):
    """Raised when a requested query does not exist."""


# Service = business logic. This one coordinates two repositories: before
# creating a query it checks (via the conversation repo) that the parent
# conversation exists, turning a would-be foreign-key error into a clean
# domain error the route can map to a 404.


class QueryService:
    def __init__(
        self, repo: QueryRepository, conversation_repo: ConversationRepository
    ):
        self.repo = repo
        self.conversation_repo = conversation_repo

    def list_queries(self) -> list[dict]:
        return self.repo.get_all()

    def get_query(self, query_id: int) -> dict:
        query = self.repo.get_by_id(query_id)
        if query is None:
            raise QueryNotFoundError(f"Query {query_id} not found")
        return query

    def list_for_conversation(self, conversation_id: int) -> list[dict]:
        if self.conversation_repo.get_by_id(conversation_id) is None:
            raise ConversationNotFoundError(
                f"Conversation {conversation_id} not found"
            )
        return self.repo.get_by_conversation(conversation_id)

    def create_query(self, data: QueryCreate) -> list[dict]:
        """Store the submitted query and return the turns that were created.

        A user input turn (is_input=True) also triggers an automatic output
        turn from the conversation's chosen LLM, so two queries come back. An
        agent output submitted directly (is_input=False) is stored as-is, so
        only that one query comes back."""
        conversation = self.conversation_repo.get_by_id(data.conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(
                f"Conversation {data.conversation_id} not found"
            )
        # An ended (rated) conversation is closed: no more input or output.
        if conversation["quality_metric"] is not None:
            raise ConversationEndedError(
                f"Conversation {data.conversation_id} has already ended"
            )

        submitted = self.repo.create(
            query_text=data.query_text,
            conversation_id=data.conversation_id,
            is_input=data.is_input,
        )
        created = [submitted]

        # Only a user input turn gets an automatic LLM reply, using the model
        # chosen for this conversation.
        if data.is_input:
            llm = get_llm(LLMType(conversation["llm_model"]))
            output = self.repo.create(
                query_text=llm.respond(data.query_text),
                conversation_id=data.conversation_id,
                is_input=False,
            )
            created.append(output)

        return created
