from http import HTTPStatus

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.application.common.exceptions import ApplicationError, ValidationError


class FieldError(BaseModel):
    field: str
    message: str


class ErrorResponse(BaseModel):
    detail: str
    status_code: int
    errors: list[FieldError] | None = None


def _error_response(
    *,
    detail: str,
    status_code: int,
    errors: list[FieldError] | None = None,
) -> JSONResponse:
    return JSONResponse(
        content=ErrorResponse(
            detail=detail,
            status_code=status_code,
            errors=errors,
        ).model_dump(exclude_none=True),
        status_code=status_code,
    )


def _format_request_validation_errors(exc: RequestValidationError) -> list[FieldError]:
    errors: list[FieldError] = []
    for error in exc.errors():
        location = [str(part) for part in error.get("loc", ()) if part != "body"]
        field = ".".join(location) if location else "request"
        errors.append(FieldError(field=field, message=error["msg"]))
    return errors


async def custom_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return _error_response(
        detail="Internal Server Error",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    )


async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return _error_response(
        detail="Request validation failed",
        status_code=HTTPStatus.BAD_REQUEST,
        errors=_format_request_validation_errors(exc),
    )


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    return _error_response(detail=exc.message, status_code=exc.status_code)


async def application_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
    return _error_response(detail=exc.message, status_code=exc.status_code)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return _error_response(detail=detail, status_code=exc.status_code)


async def value_error_handler(request: Request, exc: ValueError | TypeError) -> JSONResponse:
    return _error_response(
        detail=str(exc),
        status_code=HTTPStatus.BAD_REQUEST,
    )
