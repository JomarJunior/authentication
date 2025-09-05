from uuid import UUID
from typing import List
from src.Authentication.Domain.Interfaces import ISessionService
from src.Session.Application.CreateSession import CreateSessionHandler, CreateSessionCommand
from src.Session.Application.ValidateSession import ValidateSessionHandler, ValidateSessionCommand
from src.Shared.Models import AuthenticationMethod
from src.Shared.Enums import AuthenticationMethodEnum


class SessionService(ISessionService):
    def __init__(
        self,
        createSessionHandler: CreateSessionHandler,
        validateSessionHandler: ValidateSessionHandler,
    ):
        self.createSessionHandler = createSessionHandler
        self.validateSessionHandler = validateSessionHandler

    def CreateSession(
        self,
        userId: UUID,
        clientId: UUID,
        scopes: List[str],
        codeChallenge: str,
        authenticationMethod: AuthenticationMethod,
        authenticationCodeId: UUID | None,
    ) -> UUID:
        command = CreateSessionCommand(
            userId=userId,
            clientId=clientId,
            scopes=scopes,
            codeChallenge=codeChallenge,
            authenticationMethod=authenticationMethod,
            authenticationCodeId=authenticationCodeId,
        )
        return self.createSessionHandler.Handle(command)

    def CreatePasswordSession(
        self,
        userId: UUID,
        clientId: UUID,
        scopes: List[str],
        codeChallenge: str,
        authenticationCodeId: UUID | None,
    ) -> UUID:
        command = CreateSessionCommand(
            userId=userId,
            clientId=clientId,
            scopes=scopes,
            codeChallenge=codeChallenge,
            authenticationMethod=AuthenticationMethod(value=AuthenticationMethodEnum.PASSWORD),
            authenticationCodeId=authenticationCodeId,
        )
        return self.createSessionHandler.Handle(command)

    def CreateMFASession(
        self,
        userId: UUID,
        clientId: UUID,
        scopes: List[str],
        codeChallenge: str,
        authenticationCodeId: UUID | None,
    ) -> UUID:
        command = CreateSessionCommand(
            userId=userId,
            clientId=clientId,
            scopes=scopes,
            codeChallenge=codeChallenge,
            authenticationMethod=AuthenticationMethod(value=AuthenticationMethodEnum.MFA),
            authenticationCodeId=authenticationCodeId,
        )
        return self.createSessionHandler.Handle(command)

    def ValidateSession(
        self,
        sessionId: str,
        requiredScopes: List[str],
        clientId: str,
        codeChallenge: str,
        authenticationMethod: AuthenticationMethod,
    ) -> None:
        command = ValidateSessionCommand(
            sessionId=sessionId,
            requiredScopes=requiredScopes,
            clientId=clientId,
            codeChallenge=codeChallenge,
            authenticationMethod=authenticationMethod,
        )
        self.validateSessionHandler.Handle(command)
