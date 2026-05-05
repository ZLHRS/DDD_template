from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt

from app.config import Config

ACCESS_COOKIE_KEY = "access_jwt"
REFRESH_COOKIE_KEY = "refresh_token"
JWT_AUTH_COOKIE_PATH = "/"
JWT_AUTH_COOKIE_SAMESITE = "lax"
_SUCCESS_BODY = {"success": True}


@dataclass(frozen=True)
class AuthenticatedUserClaims:
    user_id: int
    is_admin: bool


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def _parse_user_id(subject: Any) -> int:
    try:
        user_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise _unauthorized("Invalid token subject") from exc

    if user_id <= 0:
        raise _unauthorized("Invalid token subject")
    return user_id


def decode_access_token(encoded_token: str, config: Config) -> AuthenticatedUserClaims:
    try:
        payload = jwt.decode(
            encoded_token,
            config.auth.secret_key.get_secret_value(),
            algorithms=[config.auth.algorithm],
        )
    except JWTError as exc:
        raise _unauthorized("Invalid or expired token") from exc

    subject = payload.get("sub")
    if not subject:
        raise _unauthorized("Invalid token subject")

    is_admin = payload.get("is_admin")
    if not isinstance(is_admin, bool):
        raise _unauthorized("Invalid token")

    return AuthenticatedUserClaims(user_id=_parse_user_id(subject), is_admin=is_admin)


def create_access_token(user_id: int, is_admin: bool, config: Config) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=config.auth.access_token_expire_minutes
    )
    return jwt.encode(
        {
            "sub": str(user_id),
            "is_admin": is_admin,
            "exp": expire,
        },
        config.auth.secret_key.get_secret_value(),
        algorithm=config.auth.algorithm,
    )


def _get_cookie_token(request: Request, cookie_key: str) -> str | None:
    encoded_token = request.cookies.get(cookie_key)
    if encoded_token is None:
        return None
    if not encoded_token:
        raise _unauthorized("Invalid token")
    return encoded_token


def get_auth_claims_from_request(
    request: Request,
    config: Config,
) -> AuthenticatedUserClaims | None:
    encoded_token = _get_cookie_token(request, ACCESS_COOKIE_KEY)
    if encoded_token is None:
        return None
    return decode_access_token(encoded_token=encoded_token, config=config)


def require_auth_claims_from_request(
    request: Request,
    config: Config,
) -> AuthenticatedUserClaims:
    claims = get_auth_claims_from_request(request, config)
    if claims is None:
        raise _unauthorized("Not authenticated")
    return claims


def get_refresh_token_from_request(request: Request) -> str | None:
    return _get_cookie_token(request, REFRESH_COOKIE_KEY)


def require_refresh_token_from_request(request: Request) -> str:
    refresh_token = get_refresh_token_from_request(request)
    if refresh_token is None:
        raise _unauthorized("No refresh token found in request cookies")
    return refresh_token


def create_success_response() -> JSONResponse:
    return JSONResponse(content=_SUCCESS_BODY, status_code=status.HTTP_200_OK)


def set_access_cookie(response: Response, access_token: str, config: Config) -> Response:
    response.set_cookie(
        key=ACCESS_COOKIE_KEY,
        value=access_token,
        max_age=config.auth.access_token_expire_minutes * 60,
        path=JWT_AUTH_COOKIE_PATH,
        secure=config.environment == "production",
        httponly=True,
        samesite=JWT_AUTH_COOKIE_SAMESITE,
    )
    return response


def set_refresh_cookie(response: Response, refresh_token: str, config: Config) -> Response:
    response.set_cookie(
        key=REFRESH_COOKIE_KEY,
        value=refresh_token,
        max_age=config.auth.refresh_token_expire_days * 24 * 60 * 60,
        path=JWT_AUTH_COOKIE_PATH,
        secure=config.environment == "production",
        httponly=True,
        samesite=JWT_AUTH_COOKIE_SAMESITE,
    )
    return response


def create_auth_response(
    *,
    config: Config,
    user_id: int,
    is_admin: bool,
    refresh_token: str | None = None,
) -> JSONResponse:
    response = create_success_response()
    response = set_access_cookie(
        response,
        create_access_token(user_id=user_id, is_admin=is_admin, config=config),
        config,
    )
    if refresh_token is not None:
        response = set_refresh_cookie(response, refresh_token, config)
    return response


def clear_auth_cookies(response: Response) -> Response:
    response.delete_cookie(key=ACCESS_COOKIE_KEY, path=JWT_AUTH_COOKIE_PATH)
    response.delete_cookie(key=REFRESH_COOKIE_KEY, path=JWT_AUTH_COOKIE_PATH)
    return response
