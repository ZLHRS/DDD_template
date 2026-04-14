from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, Request, Response, status
from jose import JWTError, jwt

from app.config import Config
from app.domain.user.vo import UserId

ACCESS_COOKIE_KEY = "access_jwt"
REFRESH_COOKIE_KEY = "refresh_token"
JWT_AUTH_COOKIE_PATH = "/"
JWT_AUTH_COOKIE_SAMESITE = "lax"


@dataclass(frozen=True)
class AuthenticatedUserClaims:
    user_id: UserId
    is_admin: bool



def _user_id_from_subject(subject: str) -> UserId:
    try:
        return UserId(int(subject))
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        ) from exc



def _normalize_encoded_token(encoded_token: str) -> str:
    if encoded_token.startswith("Bearer "):
        bearer_token = encoded_token[7:]
        if not bearer_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        return bearer_token
    return encoded_token



def decode_token(encoded_token: str, config: Config) -> dict[str, Any]:
    try:
        return jwt.decode(
            _normalize_encoded_token(encoded_token),
            config.auth.secret_key.get_secret_value(),
            algorithms=[config.auth.algorithm],
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc



def decode_token_to_claims(encoded_token: str, config: Config) -> AuthenticatedUserClaims:
    payload = decode_token(encoded_token, config)
    subject = payload.get("sub")
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        )

    is_admin = payload.get("is_admin")
    if not isinstance(is_admin, bool):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return AuthenticatedUserClaims(user_id=_user_id_from_subject(subject), is_admin=is_admin)



def create_access_token(user_id: UserId, is_admin: bool, config: Config) -> str:
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



def _extract_optional_cookie_token(request: Request, cookie_key: str) -> str | None:
    encoded_token = request.cookies.get(cookie_key)
    if encoded_token is None:
        return None
    if not encoded_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return encoded_token



def get_optional_auth_claims_from_request(
    request: Request,
    config: Config,
) -> AuthenticatedUserClaims | None:
    encoded_token = _extract_optional_cookie_token(request, ACCESS_COOKIE_KEY)
    if encoded_token is None:
        return None
    return decode_token_to_claims(encoded_token=encoded_token, config=config)



def get_optional_refresh_token_from_request(request: Request) -> str | None:
    return _extract_optional_cookie_token(request, REFRESH_COOKIE_KEY)



def require_refresh_token_from_request(request: Request) -> str:
    refresh_token = get_optional_refresh_token_from_request(request)
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token found in request cookies",
        )
    return refresh_token



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



def set_access_token_cookie(response: Response, access_token: str, config: Config) -> Response:
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



def clear_auth_cookies(response: Response) -> Response:
    response.delete_cookie(key=ACCESS_COOKIE_KEY, path=JWT_AUTH_COOKIE_PATH)
    response.delete_cookie(key=REFRESH_COOKIE_KEY, path=JWT_AUTH_COOKIE_PATH)
    return response
