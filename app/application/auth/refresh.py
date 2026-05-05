from dataclasses import dataclass
from datetime import UTC, datetime

from app.application.auth.exceptions import InvalidRefreshTokenError
from app.application.interfaces.auth import AuthService
from app.domain.auth import RefreshSessionRepository
from app.domain.user.repository import IUserRepository


@dataclass(frozen=True)
class RefreshResult:
    user_id: int
    is_admin: bool


class RefreshInteractor:
    def __init__(
        self,
        user_repository: IUserRepository,
        refresh_session_repository: RefreshSessionRepository,
        auth_service: AuthService,
    ) -> None:
        self.user_repository = user_repository
        self.refresh_session_repository = refresh_session_repository
        self.auth_service = auth_service

    async def __call__(self, *, refresh_token: str) -> RefreshResult:
        now = datetime.now(UTC)
        token_hash = self.auth_service.hash_refresh_token(refresh_token)
        refresh_session = await self.refresh_session_repository.get_session_by_token_hash(
            token_hash
        )
        if refresh_session is None or not refresh_session.is_active_at(now):
            raise InvalidRefreshTokenError("Invalid refresh token")

        user = await self.user_repository.get_by_id(refresh_session.user_id)
        if user is None:
            raise InvalidRefreshTokenError("Invalid refresh token")

        return RefreshResult(
            user_id=user.id,
            is_admin=user.is_admin,
        )
