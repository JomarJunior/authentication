from sqlalchemy.orm import Session as DatabaseSession
from src.Shared.DependencyInjection.Container import Container
from src.Authentication.Domain.Interfaces import IUserRepository, IHashingService
from src.Authentication.Domain.Sevices import UniquenessService
from src.Authentication.Infrastructure.Hashing import BcryptHashingService
from src.Authentication.Infrastructure.Database.SqlRepositories import SqlUserRepository
from src.Authentication.Infrastructure.Http.Controller import AuthenticationController
from src.Authentication.Application.ListAllUsers import ListAllUsersHandler
from src.Authentication.Application.RegisterUser import RegisterUserHandler
from src.Shared.Logging.Interfaces import ILogger
from src.Shared.Events.Models import EventDispatcher


class AuthenticationDependencies:
    @classmethod
    def RegisterDependencies(cls, container: Container):
        container.RegisterFactories(
            {
                # Repositories
                IUserRepository.__name__: lambda container: SqlUserRepository(
                    session=container.Get(DatabaseSession.__name__)
                ),
                # Services
                IHashingService.__name__: lambda container: BcryptHashingService(),
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
                # Controller
                AuthenticationController.__name__: lambda container: AuthenticationController(
                    listAllUsersHandler=container.Get(ListAllUsersHandler.__name__),
                    registerUserHandler=container.Get(RegisterUserHandler.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
            }
        )
