from dataclasses import dataclass
from datetime import datetime

from app.domain.user.vo import Email, UserRole


@dataclass
class User:
    id: int
    full_name: str
    email: Email
    role: UserRole
    password_hash: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_login_at: datetime | None = None