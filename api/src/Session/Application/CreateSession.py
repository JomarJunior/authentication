from uuid import UUID, uuid4
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from src.Shared.Enums import AuthenticationMethodEnum
from src.Shared.Models import AuthenticationMethod
from src.Shared.Logging.Interfaces import ILogger
from src.Shared.Events.Models import EventDispatcher
from src.Session.Domain.Interfaces import ISessionRepository
from src.Session.Domain.Models import Session


class CreateSessionCommand(BaseModel):
    userId: UUID = Field(...)
    clientId: UUID = Field(...)
    scopes: List[str] = Field(default_factory=list)
    codeChallenge: str = Field(...)
    authenticationMethod: AuthenticationMethod = Field(...)
    authenticationCodeId: Optional[UUID] = Field(None)

    @field_validator("authenticationMethod", mode="before")
    @classmethod
    def ValidateAuthenticationMethod(cls, v):
        if isinstance(v, str):
            return AuthenticationMethod(value=AuthenticationMethodEnum(v))
        return v


class CreateSessionHandler:
    def __init__(
        self,
        sessionRepository: ISessionRepository,
        eventDispatcher: EventDispatcher,
        logger: ILogger,
    ):
        self.sessionRepository = sessionRepository
        self.eventDispatcher = eventDispatcher
        self.logger = logger

    def Handle(self, command: CreateSessionCommand) -> UUID:
        # Create a new session instance
        session = Session.Create(
            id=uuid4(),
            userId=command.userId,
            clientId=command.clientId,
            scopes=command.scopes,
            codeChallenge=command.codeChallenge,
            authenticationMethod=command.authenticationMethod,
            authenticationCodeId=command.authenticationCodeId,
        )

        # Save the session to the repository
        self.sessionRepository.Save(session)

        # Dispatch any events associated with the session creation
        self.eventDispatcher.DispatchAll(session.ReleaseEvents())

        self.logger.Info(f"Session created successfully: {session.id}")
        return session.id
