from sqlalchemy.orm import Session as DatabaseSession
from src.Shared.Config.AppConfig import AppConfig
from src.Shared.DependencyInjection.Container import Container
from src.Authentication.Domain.Interfaces import (
    IUserRepository,
    IHashingService,
    IAuthCodeRepository,
    ISessionService,
)
from src.Authentication.Domain.Sevices import AuthenticationCodeService, UniquenessService
from src.Authentication.Infrastructure.Hashing import BcryptHashingService
from src.Authentication.Infrastructure.Database.SqlRepositories import (
    SqlUserRepository,
    SqlAuthCodeRepository,
)
from src.Authentication.Infrastructure.Internal import SessionService
from src.Authentication.Infrastructure.Http.Controller import AuthenticationController
from src.Authentication.Application.ListAllUsers import ListAllUsersHandler
from src.Authentication.Application.RegisterUser import RegisterUserHandler
from src.Authentication.Application.Authenticate import AuthenticateHandler
from src.Shared.Logging.Interfaces import ILogger
from src.Shared.Events.Models import EventDispatcher
from src.Session.Application.CreateSession import CreateSessionHandler
from src.Session.Application.ValidateSession import ValidateSessionHandler


class AuthenticationDependencies:
    @classmethod
    def RegisterDependencies(cls, container: Container):
        container.RegisterFactories(
            {
                # Repositories
                IUserRepository.__name__: lambda container: SqlUserRepository(
                    session=container.Get(DatabaseSession.__name__)
                ),
                IAuthCodeRepository.__name__: lambda container: SqlAuthCodeRepository(
                    session=container.Get(DatabaseSession.__name__)
                ),
                # Services
                IHashingService.__name__: lambda container: BcryptHashingService(),
                ISessionService.__name__: lambda container: SessionService(
                    createSessionHandler=container.Get(CreateSessionHandler.__name__),
                    validateSessionHandler=container.Get(ValidateSessionHandler.__name__),
                ),
                # Handlers
                ListAllUsersHandler.__name__: lambda container: ListAllUsersHandler(
                    userRepository=container.Get(IUserRepository.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
                RegisterUserHandler.__name__: lambda container: RegisterUserHandler(
                    userRepository=container.Get(IUserRepository.__name__),
                    hashingService=container.Get(IHashingService.__name__),
                    uniquenessService=UniquenessService(
                        userRepository=container.Get(IUserRepository.__name__)
                    ),
                    logger=container.Get(ILogger.__name__),
                    eventDispatcher=container.Get(EventDispatcher.__name__),
                ),
                AuthenticateHandler.__name__: lambda container: AuthenticateHandler(
                    userRepository=container.Get(IUserRepository.__name__),
                    authCodeRepository=container.Get(IAuthCodeRepository.__name__),
                    hashingService=container.Get(IHashingService.__name__),
                    authenticationCodeService=AuthenticationCodeService(
                        appConfig=container.Get(AppConfig.__name__),
                    ),
                    sessionService=container.Get(ISessionService.__name__),
                    eventDispatcher=container.Get(EventDispatcher.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
                # Controller
                AuthenticationController.__name__: lambda container: AuthenticationController(
                    listAllUsersHandler=container.Get(ListAllUsersHandler.__name__),
                    registerUserHandler=container.Get(RegisterUserHandler.__name__),
                    authenticateHandler=container.Get(AuthenticateHandler.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
            }
        )
