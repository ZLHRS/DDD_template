from dishka import Provider, Scope, provide

from app.application.interfaces.auth import AuthService
from app.infrastructure.auth import AuthServiceImpl


class AuthProvider(Provider):
    scope = Scope.APP

    @provide(scope=Scope.APP)
    def provide_auth_service(self) -> AuthService:
        return AuthServiceImpl()
