from sqlalchemy.orm import Session as DatabaseSession
from src.Shared.DependencyInjection.Container import Container
from src.Session.Domain.Interfaces import ISessionRepository
from src.Session.Infrastructure.Database.SqlRepositories import SqlSessionRepository
from src.Session.Application.CreateSession import CreateSessionHandler
from src.Session.Application.ValidateSession import ValidateSessionHandler
from src.Session.Infrastructure.Http.Controller import SessionController
from src.Shared.Logging.Interfaces import ILogger
from src.Shared.Events.Models import EventDispatcher


class SessionDependencies:
    @staticmethod
    def RegisterDependencies(container: Container):
        container.RegisterFactories(
            {
                # Repositories
                ISessionRepository.__name__: lambda container: SqlSessionRepository(
                    session=container.Get(DatabaseSession.__name__)
                ),
                # Services
                # Handlers
                CreateSessionHandler.__name__: lambda container: CreateSessionHandler(
                    sessionRepository=container.Get(ISessionRepository.__name__),
                    logger=container.Get(ILogger.__name__),
                    eventDispatcher=container.Get(EventDispatcher.__name__),
                ),
                ValidateSessionHandler.__name__: lambda container: ValidateSessionHandler(
                    sessionRepository=container.Get(ISessionRepository.__name__),
                    eventDispatcher=container.Get(EventDispatcher.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
                # Controller
                SessionController.__name__: lambda container: SessionController(
                    createSessionHandler=container.Get(CreateSessionHandler.__name__),
                    validateSessionHandler=container.Get(ValidateSessionHandler.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
            }
        )
