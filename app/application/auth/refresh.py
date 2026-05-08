from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.application.auth.exceptions import InvalidRefreshTokenError
from app.application.interfaces.auth import AuthService
from app.domain.auth import RefreshSession, RefreshSessionRepository
from app.domain.user.repository import IUserRepository
from app.domain.user.vo import UserRole


@dataclass(frozen=True)
class RefreshResult:
    user_id: int
    role: UserRole
    refresh_token: str


class RefreshInteractor:
    def __init__(
        self,
        user_repository: IUserRepository,
        refresh_session_repository: RefreshSessionRepository,
        auth_service: AuthService,
        refresh_token_expire_days: int,
    ) -> None:
        self.user_repository = user_repository
        self.refresh_session_repository = refresh_session_repository
        self.auth_service = auth_service
        self.refresh_token_expire_days = refresh_token_expire_days

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

        revoked_session = await self.refresh_session_repository.revoke_session(
            token_hash=token_hash,
            revoked_at=now,
        )
        if revoked_session is None:
            raise InvalidRefreshTokenError("Invalid refresh token")

        next_refresh_token = self.auth_service.create_refresh_token()
        next_refresh_session = RefreshSession(
            token_hash=self.auth_service.hash_refresh_token(next_refresh_token),
            user_id=user.id,
            expires_at=now + timedelta(days=self.refresh_token_expire_days),
            created_at=now,
            revoked_at=None,
        )
        await self.refresh_session_repository.create_session(next_refresh_session)

        return RefreshResult(
            user_id=user.id,
            role=user.role,
            refresh_token=next_refresh_token,
        )