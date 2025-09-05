import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID
from src.Authentication.Domain.Interfaces import IUserRepository
from src.Shared.Config.AppConfig import AppConfig
from src.Authentication.Domain.Models import AuthenticationCode


class UniquenessService:
    def __init__(self, userRepository: IUserRepository):
        self.userRepository = userRepository

    def ValidateIsEmailUnique(self, email: str) -> None:
        if self.userRepository.FindByEmail(email) is not None:
            raise ValueError("Email already in use")

    def ValidateIsUsernameUnique(self, username: str) -> None:
        if self.userRepository.FindByUsername(username) is not None:
            raise ValueError("Username already in use")


class AuthenticationCodeService:
    def __init__(self, appConfig: AppConfig):
        self.appConfig = appConfig

    def Generate(
        self, userId: UUID, clientId: UUID, scopes: List[str], codeChallenge: Optional[str] = None
    ) -> AuthenticationCode:
        authenticationCode: str = secrets.token_urlsafe(32)

        expiresAt = datetime.now(timezone.utc) + timedelta(
            minutes=self.appConfig.authCodeExpiryMinutes
        )

        return AuthenticationCode.Create(
            code=authenticationCode,
            userId=userId,
            clientId=clientId,
            scopes=scopes,
            expiresAt=expiresAt,
            codeChallenge=codeChallenge,
        )
