from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.config import Config
from app.domain.auth import RefreshSessionRepository
from app.domain.user.repository import IUserRepository
from app.infrastructure.db.factory import create_engine, create_session_maker
from app.infrastructure.db.repos import RefreshSessionRepositoryImpl, UserRepositoryImpl


class DBProvider(Provider):
    scope = Scope.APP

    @provide(scope=Scope.APP)
    def get_engine(self, config: Config) -> AsyncEngine:
        return create_engine(
            config.postgres,
            application_name="backend-template",
        )

    @provide(scope=Scope.APP)
    def get_session_maker(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return create_session_maker(engine)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self,
        session_maker: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AsyncSession]:
        async with session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            else:
                await session.commit()

    @provide(scope=Scope.REQUEST)
    async def get_user_repository(
        self,
        session: AsyncSession,
    ) -> IUserRepository:
        return UserRepositoryImpl(session)

    @provide(scope=Scope.REQUEST)
    async def get_refresh_session_repository(
        self,
        session: AsyncSession,
    ) -> RefreshSessionRepository:
        return RefreshSessionRepositoryImpl(session)