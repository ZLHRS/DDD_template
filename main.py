from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from dishka.integrations.fastapi import setup_dishka

from app.application.common.exceptions import ApplicationError, ValidationError
from app.config import load_config
from app.infrastructure.container import setup_dishka_container
from app.presentation.api.auth.router import auth_router
from app.presentation.api.exception import (
    application_error_handler,
    custom_exception_handler,
    http_exception_handler,
    request_validation_exception_handler,
    validation_error_handler,
    value_error_handler,
)
from app.presentation.api.health.router import health_router
from app.presentation.api.user.router import user_router


def create_app() -> FastAPI:
    config = load_config()

    app = FastAPI(title="Backend Template API")

    container = setup_dishka_container(config)
    setup_dishka(container, app)

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(user_router)

    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(ApplicationError, application_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(TypeError, value_error_handler)
    app.add_exception_handler(Exception, custom_exception_handler)

    return app


app = create_app()
