from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import get_conversation_service, get_query_service
from app.models.conversation import (
    Conversation,
    ConversationEnd,
    ConversationStart,
)
from app.models.query import Query
from app.services.conversation_service import (
    ConversationEndedError,
    ConversationNotFoundError,
    ConversationService,
)
from app.services.query_service import QueryService

router = APIRouter(prefix="/conversations", tags=["conversations"])

# Routes stay thin: validate input (Pydantic), call the service, translate
# domain errors into HTTP responses. No SQL, no business rules here.


@router.get("", response_model=list[Conversation])
def list_conversations(
    service: ConversationService = Depends(get_conversation_service),
):
    return service.list_conversations()


@router.get("/{conversation_id}", response_model=Conversation)
def get_conversation(
    conversation_id: int,
    service: ConversationService = Depends(get_conversation_service),
):
    try:
        return service.get_conversation(conversation_id)
    except ConversationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/start", response_model=Conversation, status_code=status.HTTP_201_CREATED
)
def start_conversation(
    payload: ConversationStart | None = None,
    service: ConversationService = Depends(get_conversation_service),
):
    # Body is optional: omit it (or send {}) to use the default LLM (A). The
    # chosen model is fixed on the conversation for its whole life. Returns the
    # new conversation so the client gets its id to attach queries to.
    if payload is None:
        payload = ConversationStart()
    return service.start_conversation(payload.llm_type)


@router.post("/{conversation_id}/end", response_model=Conversation)
def end_conversation(
    conversation_id: int,
    payload: ConversationEnd,
    service: ConversationService = Depends(get_conversation_service),
):
    # End (rate) the conversation. After this, no more queries can be added.
    try:
        return service.end_conversation(conversation_id, payload.quality_metric)
    except ConversationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConversationEndedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{conversation_id}/queries", response_model=list[Query])
def list_conversation_queries(
    conversation_id: int,
    service: QueryService = Depends(get_query_service),
):
    try:
        return service.list_for_conversation(conversation_id)
    except ConversationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
