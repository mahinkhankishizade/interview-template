from app.models.user import UserCreate
from app.repositories.user_repository import UserRepository


class UserAlreadyExistsError(Exception):
    """Raised when trying to create a user whose email is taken."""


class UserNotFoundError(Exception):
    """Raised when a requested user does not exist."""


# Service = business logic. It orchestrates the repository, enforces rules
# that go beyond schema validation, and raises domain errors. Routes stay
# thin; repos stay dumb (just SQL). If a use case needs several tables, this
# is where you'd coordinate them (and manage a transaction).


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def list_users(self) -> list[dict]:
        return self.repo.get_all()

    def get_user(self, user_id: int) -> dict:
        user = self.repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")
        return user

    def create_user(self, data: UserCreate) -> dict:
        if self.repo.get_by_email(data.email) is not None:
            raise UserAlreadyExistsError(f"Email {data.email} is already registered")
        return self.repo.create(email=data.email, full_name=data.full_name)
