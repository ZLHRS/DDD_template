from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

from app.domain.user.vo import Email


class EmailType(TypeDecorator):
    impl = String(320)
    cache_ok = True

    def process_bind_param(self, value: Email | str | None, dialect):
        if value is None:
            return None
        if isinstance(value, Email):
            return value.value
        return value

    def process_result_value(self, value: str | None, dialect) -> Email | None:
        if value is None:
            return None
        return Email(value)
