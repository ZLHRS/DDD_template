from dishka import Provider

from .auth import AuthInteractorProvider
from .user import UserInteractorProvider

interactor_providers: list[type[Provider]] = [
    AuthInteractorProvider,
    UserInteractorProvider,
]

__all__ = [
    "AuthInteractorProvider",
    "UserInteractorProvider",
    "interactor_providers",
]
