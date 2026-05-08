from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.transaction import TransactionManager


class TransactionManagerImpl(TransactionManager):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def flush(self) -> None:
        await self.session.flush()

    async def rollback(self) -> None:
        await self.session.rollback()
