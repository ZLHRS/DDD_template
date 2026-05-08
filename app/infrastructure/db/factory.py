from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import PostgresConfig


def create_engine(
    db_config: PostgresConfig,
    *,
    application_name: str | None = None,
) -> AsyncEngine:
    connect_args = None
    if application_name is not None:
        connect_args = {"server_settings": {"application_name": application_name}}

    return create_async_engine(
        db_config.get_url(),
        echo=db_config.echo,
        pool_size=db_config.pool_size,
        pool_timeout=db_config.pool_timeout,
        pool_recycle=db_config.pool_recycle,
        max_overflow=db_config.max_overflow,
        pool_pre_ping=db_config.pool_pre_ping,
        echo_pool=db_config.echo_pool,
        connect_args=connect_args,
    )


def create_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
    )