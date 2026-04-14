from dishka import Provider, Scope, provide

from app.application.user.get_me import GetUserProfileInteractor
from app.domain.user.repository import IUserRepository


class UserInteractorProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_user_profile_interactor(
        self,
        user_repository: IUserRepository,
    ) -> GetUserProfileInteractor:
        return GetUserProfileInteractor(user_repository)
