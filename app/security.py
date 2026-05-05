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
class AuthClaims:
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


def _read_cookie(request: Request, key: str) -> str | None:
    value = request.cookies.get(key)
    if value is None:
        return None
    if not value:
        raise _unauthorized("Invalid token")
    return value


def _set_cookie(
    response: Response,
    *,
    key: str,
    value: str,
    max_age: int,
    config: Config,
) -> Response:
    response.set_cookie(
        key=key,
        value=value,
        max_age=max_age,
        path=JWT_AUTH_COOKIE_PATH,
        secure=config.environment == "production",
        httponly=True,
        samesite=JWT_AUTH_COOKIE_SAMESITE,
    )
    return response


def parse_access_token(token: str, config: Config) -> AuthClaims:
    try:
        payload = jwt.decode(
            token,
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

    return AuthClaims(user_id=_parse_user_id(subject), is_admin=is_admin)


def issue_access_token(user_id: int, is_admin: bool, config: Config) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=config.auth.access_token_expire_minutes
    )
    return jwt.encode(
        {
            "sub": str(user_id),
            "is_admin": is_admin,
            "exp": expires_at,
        },
        config.auth.secret_key.get_secret_value(),
        algorithm=config.auth.algorithm,
    )


def read_auth_claims(request: Request, config: Config) -> AuthClaims | None:
    token = _read_cookie(request, ACCESS_COOKIE_KEY)
    if token is None:
        return None
    return parse_access_token(token, config)


def require_auth_claims(request: Request, config: Config) -> AuthClaims:
    claims = read_auth_claims(request, config)
    if claims is None:
        raise _unauthorized("Not authenticated")
    return claims


def read_refresh_token(request: Request) -> str | None:
    return _read_cookie(request, REFRESH_COOKIE_KEY)


def require_refresh_token(request: Request) -> str:
    refresh_token = read_refresh_token(request)
    if refresh_token is None:
        raise _unauthorized("No refresh token found in request cookies")
    return refresh_token


def build_success_response() -> JSONResponse:
    return JSONResponse(content=_SUCCESS_BODY, status_code=status.HTTP_200_OK)


def build_auth_response(
    *,
    config: Config,
    user_id: int,
    is_admin: bool,
    refresh_token: str | None = None,
) -> JSONResponse:
    response = build_success_response()
    response = _set_cookie(
        response,
        key=ACCESS_COOKIE_KEY,
        value=issue_access_token(user_id=user_id, is_admin=is_admin, config=config),
        max_age=config.auth.access_token_expire_minutes * 60,
        config=config,
    )
    if refresh_token is not None:
        response = _set_cookie(
            response,
            key=REFRESH_COOKIE_KEY,
            value=refresh_token,
            max_age=config.auth.refresh_token_expire_days * 24 * 60 * 60,
            config=config,
        )
    return response


def clear_auth_cookies(response: Response) -> Response:
    response.delete_cookie(key=ACCESS_COOKIE_KEY, path=JWT_AUTH_COOKIE_PATH)
    response.delete_cookie(key=REFRESH_COOKIE_KEY, path=JWT_AUTH_COOKIE_PATH)
    return response
