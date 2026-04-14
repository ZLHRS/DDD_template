from fastapi import APIRouter, HTTPException, Request, Response, status
from dishka.integrations.fastapi import FromDishka, inject

from app.application.auth.login import LoginInputDTO, LoginInteractor
from app.application.auth.logout import LogoutInputDTO, LogoutInteractor
from app.application.auth.refresh import RefreshInputDTO, RefreshInteractor
from app.application.auth.register import RegisterInputDTO, RegisterInteractor
from app.application.common.transaction import TransactionManager
from app.domain.user.vo import UserId
from app.config import Config
from app.security import (
    clear_auth_cookies,
    create_access_token,
    get_optional_auth_claims_from_request,
    get_optional_refresh_token_from_request,
    require_refresh_token_from_request,
    set_access_token_cookie,
    set_refresh_cookie,
)

from .schemas import LoginRequest, RegisterRequest, SuccessResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
@inject
async def register_user_handler(
    data: RegisterRequest,
    interactor: FromDishka[RegisterInteractor],
    transaction_manager: FromDishka[TransactionManager],
) -> SuccessResponse:
    await interactor(
        RegisterInputDTO(
            email=data.email,
            password=data.password,
            full_name=data.full_name,
        )
    )
    await transaction_manager.commit()
    return SuccessResponse(success=True)


@router.post("/login", response_model=SuccessResponse)
@inject
async def login_user_handler(
    data: LoginRequest,
    interactor: FromDishka[LoginInteractor],
    transaction_manager: FromDishka[TransactionManager],
    config: FromDishka[Config],
) -> Response:
    login_result = await interactor(
        LoginInputDTO(
            email=data.email,
            password=data.password,
        )
    )
    await transaction_manager.commit()

    access_token = create_access_token(
        user_id=UserId(login_result.user_id),
        is_admin=login_result.is_admin,
        config=config,
    )

    response = Response(
        content='{"success": true}',
        status_code=status.HTTP_200_OK,
        media_type="application/json",
    )
    response = set_access_token_cookie(response, access_token, config)
    response = set_refresh_cookie(response, login_result.refresh_token, config)
    return response


@router.post("/refresh", response_model=SuccessResponse)
@inject
async def refresh_user_handler(
    request: Request,
    interactor: FromDishka[RefreshInteractor],
    config: FromDishka[Config],
) -> Response:
    refresh_result = await interactor(
        RefreshInputDTO(refresh_token=require_refresh_token_from_request(request))
    )

    access_token = create_access_token(
        user_id=UserId(refresh_result.user_id),
        is_admin=refresh_result.is_admin,
        config=config,
    )

    response = Response(
        content='{"success": true}',
        status_code=status.HTTP_200_OK,
        media_type="application/json",
    )
    return set_access_token_cookie(response, access_token, config)


@router.post("/logout", response_model=SuccessResponse)
@inject
async def logout_user_handler(
    request: Request,
    interactor: FromDishka[LogoutInteractor],
    transaction_manager: FromDishka[TransactionManager],
    config: FromDishka[Config],
) -> Response:
    if get_optional_auth_claims_from_request(request, config) is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    await interactor(
        LogoutInputDTO(
            refresh_token=get_optional_refresh_token_from_request(request),
        )
    )
    await transaction_manager.commit()

    response = Response(
        content='{"success": true}',
        status_code=status.HTTP_200_OK,
        media_type="application/json",
    )
    return clear_auth_cookies(response)


auth_router = router
