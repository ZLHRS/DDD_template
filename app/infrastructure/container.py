from dishka import make_async_container

from app.config import Config
from app.infrastructure.di.auth import AuthProvider
from app.infrastructure.di.config import ConfigProvider
from app.infrastructure.di.db import DBProvider
from app.infrastructure.di.interactors import interactor_providers



def setup_dishka_container(config: Config):
    return make_async_container(
        ConfigProvider(config),
        DBProvider(),
        AuthProvider(),
        *[provider() for provider in interactor_providers],
    )
