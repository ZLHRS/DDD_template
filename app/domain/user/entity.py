from dataclasses import dataclass
from datetime import datetime

from app.domain.user.vo import Email, UserRole


@dataclass(kw_only=True)
class User:
    full_name: str
    email: Email
    role: UserRole
    password_hash: str
    id: int | None = None
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_login_at: datetime | None = None