from typing import Protocol

from app.domain.user.entity import User
from app.domain.user.vo import Email


class IUserRepository(Protocol):
    async def get_by_id(self, user_id: int) -> User | None: ...

    async def get_by_email(self, email: Email) -> User | None: ...

    async def create_user(self, user: User) -> User: ...

    async def update_user(self, user: User) -> User: ...
