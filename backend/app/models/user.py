from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Request body for creating a user."""

    email: EmailStr
    full_name: str


class User(BaseModel):
    """Response shape for a user."""

    id: int
    email: EmailStr
    full_name: str
    created_at: datetime
