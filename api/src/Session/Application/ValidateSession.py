from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from src.Session.Domain.Interfaces import ISessionRepository
from src.Shared.Enums import AuthenticationMethodEnum
from src.Shared.Logging.Interfaces import ILogger
from src.Session.Domain.Models import Session
from src.Session.Domain.Services import SessionValidationService
from src.Shared.Events.Models import EventDispatcher
from src.Shared.Models import AuthenticationMethod


class ValidateSessionCommand(BaseModel):
    sessionId: Optional[UUID] = Field(None)
    userId: UUID = Field(...)
    requiredScopes: List[str] = Field(default_factory=list)
    clientId: UUID = Field(...)
    codeChallenge: str = Field(min_length=43, max_length=128)
    authenticationMethod: AuthenticationMethod = Field(...)

    @field_validator("authenticationMethod", mode="before")
    @classmethod
    def ValidateAuthenticationMethod(cls, v):
        if isinstance(v, str):
            return AuthenticationMethod(value=AuthenticationMethodEnum(v))
        return v


class ValidateSessionHandler:
    def __init__(
        self,
        sessionRepository: ISessionRepository,
        eventDispatcher: EventDispatcher,
        logger: ILogger,
    ):
        self.sessionRepository = sessionRepository
        self.eventDispatcher = eventDispatcher
        self.logger = logger

    def Handle(self, command: ValidateSessionCommand) -> None:
        if not command.sessionId:
            raise ValueError("sessionId is required")

        # Find the session by ID
        session: Optional[Session] = self.sessionRepository.FindById(command.sessionId)
        if not session:
            self.logger.Warning(f"Session not found: {command.sessionId}")
            raise ValueError("Session not found")

        # Validate the session using the domain service
        SessionValidationService.ValidateSession(
            session,
            command.userId,
            command.requiredScopes,
            command.clientId,
            command.codeChallenge,
            command.authenticationMethod.value,
        )

        self.logger.Info(f"Session validated successfully: {command.sessionId}")
