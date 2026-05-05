from dataclasses import dataclass

from app.application.user.exceptions import UserNotFoundError
from app.domain.user.repository import IUserRepository


@dataclass(frozen=True)
class GetUserProfileOutputDTO:
    id: int
    email: str
    full_name: str
    is_admin: bool


class GetUserProfileInteractor:
    def __init__(self, user_repository: IUserRepository) -> None:
        self.user_repository = user_repository

    async def __call__(self, *, user_id: int) -> GetUserProfileOutputDTO:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)

        return GetUserProfileOutputDTO(
            id=user.id,
            email=user.email.value,
            full_name=user.full_name,
            is_admin=user.is_admin,
        )
