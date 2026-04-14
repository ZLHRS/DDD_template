from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.user.vo import Email, PasswordHash, UserId, UserRole


@dataclass
class User:
    id: UserId
    full_name: str
    email: Email
    role: UserRole
    password_hash: PasswordHash
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_login_at: datetime | None = None

    def has_role(self, role: UserRole) -> bool:
        return self.role == role

    def deactivate(self) -> None:
        self.is_active = False

    @classmethod
    def create(
        cls,
        user_id: str,
        full_name: str,
        email: str,
        role: UserRole,
        password_hash: PasswordHash,
    ) -> "User":
        now = datetime.now(UTC)
        return cls(
            id=UserId(user_id),
            full_name=full_name,
            email=Email(email),
            role=role,
            password_hash=password_hash,
            is_admin=False,
            created_at=now,
            updated_at=now,
        )
