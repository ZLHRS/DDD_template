from fastapi import APIRouter, Request, status
from dishka.integrations.fastapi import FromDishka, inject

from app.application.user.get_me import GetUserProfileInteractor, GetUserProfileOutputDTO
from app.config import Config
from app.security import require_auth_claims

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=GetUserProfileOutputDTO, status_code=status.HTTP_200_OK)
@inject
async def get_user_profile(
    request: Request,
    interactor: FromDishka[GetUserProfileInteractor],
    config: FromDishka[Config],
) -> GetUserProfileOutputDTO:
    claims = require_auth_claims(request, config)
    return await interactor(user_id=claims.user_id)


user_router = router
