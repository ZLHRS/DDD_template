from datetime import datetime

from sqlalchemy import BIGINT, TIMESTAMP, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORMModel


class RefreshSessionModel(BaseORMModel):
    __tablename__ = "refresh_sessions"

    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
