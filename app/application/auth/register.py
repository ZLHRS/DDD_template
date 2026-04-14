from dataclasses import dataclass
from datetime import UTC, datetime
import secrets

from app.application.common.exceptions import ValidationError
from app.application.common.interactor import Interactor
from app.application.interfaces.auth import AuthService
from app.domain.user.entity import User
from app.domain.user.repository import IUserRepository
from app.domain.user.vo import Email, PasswordHash, UserId, UserRole


@dataclass
class RegisterInputDTO:
    email: str
    password: str
    full_name: str


@dataclass
class RegisterOutputDTO:
    user_id: UserId
    email: str


class RegisterInteractor(Interactor[RegisterInputDTO, RegisterOutputDTO]):
    def __init__(
        self,
        user_repository: IUserRepository,
        auth_service: AuthService,
    ) -> None:
        self.user_repository = user_repository
        self.auth_service = auth_service

    async def __call__(self, data: RegisterInputDTO) -> RegisterOutputDTO:
        email = Email(data.email)
        full_name = data.full_name.strip()

        if len(data.password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        if not full_name:
            raise ValidationError("Full name must not be empty")

        existing_user = await self.user_repository.get_by_email(email)
        if existing_user is not None:
            raise ValidationError("Email already registered")

        now = datetime.now(UTC)
        user = User(
            id=UserId(secrets.randbelow(2**63 - 1) + 1),
            email=email,
            password_hash=PasswordHash(self.auth_service.hash_password(data.password)),
            full_name=full_name,
            role=UserRole.ANALYST,
            is_admin=False,
            created_at=now,
            updated_at=now,
            last_login_at=None,
        )
        await self.user_repository.create_user(user)

        return RegisterOutputDTO(user_id=user.id, email=user.email.value)
