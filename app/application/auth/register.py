from datetime import UTC, datetime

from app.application.common.exceptions import ValidationError
from app.application.interfaces.auth import AuthService
from app.domain.user.entity import User
from app.domain.user.repository import IUserRepository
from app.domain.user.vo import Email, UserRole


class RegisterInteractor:
    def __init__(
        self,
        user_repository: IUserRepository,
        auth_service: AuthService,
    ) -> None:
        self.user_repository = user_repository
        self.auth_service = auth_service

    async def __call__(self, *, email: str, password: str, full_name: str) -> None:
        normalized_email = Email(email)
        existing_user = await self.user_repository.get_by_email(normalized_email)
        if existing_user is not None:
            raise ValidationError("Email already registered")

        now = datetime.now(UTC)
        user = User(
            email=normalized_email,
            password_hash=self.auth_service.hash_password(password),
            full_name=full_name,
            role=UserRole.USER,
            created_at=now,
            updated_at=now,
            last_login_at=None,
        )
        await self.user_repository.create_user(user)