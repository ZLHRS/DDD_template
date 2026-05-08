from fastapi import APIRouter, Request, Response, status
from dishka.integrations.fastapi import FromDishka, inject

from app.application.auth.login import LoginInteractor
from app.application.auth.logout import LogoutInteractor
from app.application.auth.refresh import RefreshInteractor
from app.application.auth.register import RegisterInteractor
from app.config import Config
from app.security import (
    build_auth_response,
    build_success_response,
    clear_auth_cookies,
    read_refresh_token,
    require_auth_claims,
    require_refresh_token,
)

from .schemas import LoginRequest, RegisterRequest, SuccessResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
@inject
async def register_user_handler(
    data: RegisterRequest,
    interactor: FromDishka[RegisterInteractor],
) -> SuccessResponse:
    await interactor(email=data.email, password=data.password, full_name=data.full_name)
    return SuccessResponse(success=True)


@router.post("/login", response_model=SuccessResponse)
@inject
async def login_user_handler(
    data: LoginRequest,
    interactor: FromDishka[LoginInteractor],
    config: FromDishka[Config],
) -> Response:
    login_result = await interactor(email=data.email, password=data.password)
    return build_auth_response(
        config=config,
        user_id=login_result.user_id,
        role=login_result.role,
        refresh_token=login_result.refresh_token,
    )


@router.post("/refresh", response_model=SuccessResponse)
@inject
async def refresh_user_handler(
    request: Request,
    interactor: FromDishka[RefreshInteractor],
    config: FromDishka[Config],
) -> Response:
    refresh_result = await interactor(refresh_token=require_refresh_token(request))
    return build_auth_response(
        config=config,
        user_id=refresh_result.user_id,
        role=refresh_result.role,
        refresh_token=refresh_result.refresh_token,
    )


@router.post("/logout", response_model=SuccessResponse)
@inject
async def logout_user_handler(
    request: Request,
    interactor: FromDishka[LogoutInteractor],
    config: FromDishka[Config],
) -> Response:
    require_auth_claims(request, config)
    await interactor(refresh_token=read_refresh_token(request))
    return clear_auth_cookies(build_success_response())


auth_router = router
