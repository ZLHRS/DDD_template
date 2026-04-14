from sqlalchemy import select

from app.domain.user.entity import User
from app.domain.user.repository import IUserRepository
from app.domain.user.vo import Email, UserId
from app.infrastructure.db.mappers import UserMapper
from app.infrastructure.db.models.user import UserModel
from app.infrastructure.db.repos.base import BaseSQLAlchemyRepo


class UserRepositoryImpl(IUserRepository, BaseSQLAlchemyRepo):
    async def get_by_id(self, user_id: UserId) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        user_model = result.scalars().first()
        return UserMapper.to_domain(user_model) if user_model else None

    async def get_by_email(self, email: Email) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        user_model = result.scalars().first()
        return UserMapper.to_domain(user_model) if user_model else None

    async def create_user(self, user: User) -> User:
        user_model = UserMapper.to_model(user)
        self._session.add(user_model)
        await self._session.flush()
        return UserMapper.to_domain(user_model)

    async def update_user(self, user: User) -> User:
        user_model = UserMapper.to_model(user)
        merged_model = await self._session.merge(user_model)
        await self._session.flush()
        return UserMapper.to_domain(merged_model)
