from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import get_query_service
from app.models.query import Query, QueryCreate
from app.services.conversation_service import (
    ConversationEndedError,
    ConversationNotFoundError,
)
from app.services.query_service import QueryNotFoundError, QueryService

router = APIRouter(prefix="/queries", tags=["queries"])

# Routes stay thin: validate input (Pydantic), call the service, translate
# domain errors into HTTP responses. No SQL, no business rules here.


@router.get("", response_model=list[Query])
def list_queries(service: QueryService = Depends(get_query_service)):
    return service.list_queries()


@router.get("/{query_id}", response_model=Query)
def get_query(query_id: int, service: QueryService = Depends(get_query_service)):
    try:
        return service.get_query(query_id)
    except QueryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "", response_model=list[Query], status_code=status.HTTP_201_CREATED
)
def create_query(
    payload: QueryCreate, service: QueryService = Depends(get_query_service)
):
    # Returns the created turns: an input submission yields [input, output]
    # (the LLM reply), an agent output submission yields just [output].
    try:
        return service.create_query(payload)
    except ConversationNotFoundError as e:
        # The parent conversation must exist first.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConversationEndedError as e:
        # The conversation has ended: no more input or output allowed.
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
