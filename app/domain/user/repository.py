from abc import ABC, abstractmethod

from app.domain.user.entity import User
from app.domain.user.vo import Email, UserId


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: Email) -> User | None: ...

    @abstractmethod
    async def create_user(self, user: User) -> User: ...

    @abstractmethod
    async def update_user(self, user: User) -> User: ...
