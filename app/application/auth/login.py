from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta

from app.application.auth.exceptions import InvalidAuthDataError
from app.application.interfaces.auth import AuthService
from app.domain.auth import RefreshSession, RefreshSessionRepository
from app.domain.user.repository import IUserRepository
from app.domain.user.vo import Email


@dataclass(frozen=True)
class LoginResult:
    user_id: int
    is_admin: bool
    refresh_token: str


class LoginInteractor:
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

    async def __call__(self, *, email: str, password: str) -> LoginResult:
        user = await self.user_repository.get_by_email(Email(email))
        if user is None:
            raise InvalidAuthDataError("Invalid credentials")

        if not self.auth_service.verify_password(password, user.password_hash):
            raise InvalidAuthDataError("Invalid credentials")

        now = datetime.now(UTC)
        updated_user = replace(user, updated_at=now, last_login_at=now)
        updated_user = await self.user_repository.update_user(updated_user)

        refresh_token = self.auth_service.create_refresh_token()
        refresh_session = RefreshSession(
            token_hash=self.auth_service.hash_refresh_token(refresh_token),
            user_id=updated_user.id,
            expires_at=now + timedelta(days=self.refresh_token_expire_days),
            created_at=now,
            revoked_at=None,
        )
        await self.refresh_session_repository.create_session(refresh_session)

        return LoginResult(
            user_id=updated_user.id,
            is_admin=updated_user.is_admin,
            refresh_token=refresh_token,
        )
