from fastapi import Depends
from psycopg import Connection

from app.db import get_conn
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

# Dependency wiring: connection -> repository -> service.
# FastAPI resolves this chain per request, so routes just ask for a
# UserService and get one backed by a live pooled connection.


def get_user_service(conn: Connection = Depends(get_conn)) -> UserService:
    return UserService(UserRepository(conn))
