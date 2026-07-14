from fastapi import Depends
from psycopg import Connection

from app.db import get_conn
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.query_repository import QueryRepository
from app.repositories.user_repository import UserRepository
from app.services.conversation_service import ConversationService
from app.services.query_service import QueryService
from app.services.user_service import UserService

# Dependency wiring: connection -> repository -> service.
# FastAPI resolves this chain per request, so routes just ask for a
# service and get one backed by a live pooled connection.


def get_user_service(conn: Connection = Depends(get_conn)) -> UserService:
    return UserService(UserRepository(conn))


def get_conversation_service(
    conn: Connection = Depends(get_conn),
) -> ConversationService:
    return ConversationService(ConversationRepository(conn))


def get_query_service(conn: Connection = Depends(get_conn)) -> QueryService:
    # QueryService needs the conversation repo too, to validate the parent
    # conversation exists before inserting a query.
    return QueryService(QueryRepository(conn), ConversationRepository(conn))
