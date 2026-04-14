from fastapi import APIRouter, Request, status
from dishka.integrations.fastapi import FromDishka, inject

from app.application.user.get_me import (
    GetUserProfileInputDTO,
    GetUserProfileInteractor,
    GetUserProfileOutputDTO,
)
from app.config import Config
from app.security import get_optional_auth_claims_from_request

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=GetUserProfileOutputDTO, status_code=status.HTTP_200_OK)
@inject
async def get_user_profile(
    request: Request,
    interactor: FromDishka[GetUserProfileInteractor],
    config: FromDishka[Config],
) -> GetUserProfileOutputDTO:
    claims = get_optional_auth_claims_from_request(request, config)
    if claims is None:
        raise ValueError("Authentication is required")

    return await interactor(GetUserProfileInputDTO(user_id=claims.user_id))


user_router = router
