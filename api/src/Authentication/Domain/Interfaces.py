from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.Authentication.Domain.Models import User, AuthenticationCode
from src.Shared.Models import AuthenticationMethod


class IUserRepository(ABC):
    @abstractmethod
    def FindById(self, id: UUID) -> Optional[User]:
        pass

    @abstractmethod
    def FindByEmail(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def FindByUsername(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    def ListAll(self, sortBy: str, sortOrder: str, limit: int, offset: int) -> list[User]:
        pass

    @abstractmethod
    def Save(self, user: User) -> None:
        pass


class IAuthCodeRepository(ABC):
    @abstractmethod
    def FindByCode(self, code: str) -> Optional[AuthenticationCode]:
        pass

    @abstractmethod
    def Save(self, authenticationCode: AuthenticationCode) -> None:
        pass


class IHashingService(ABC):
    @abstractmethod
    def Hash(self, plainText: str) -> str:
        pass

    @abstractmethod
    def Verify(self, plainText: str, hashed: str) -> bool:
        pass


class ISessionService(ABC):
    @abstractmethod
    def CreateSession(
        self,
        userId: UUID,
        clientId: UUID,
        scopes: List[str],
        codeChallenge: str,
        authenticationMethod: AuthenticationMethod,
        authenticationCodeId: Optional[UUID],
    ) -> UUID:
        pass

    @abstractmethod
    def CreatePasswordSession(
        self,
        userId: UUID,
        clientId: UUID,
        scopes: List[str],
        codeChallenge: str,
        authenticationCodeId: Optional[UUID],
    ) -> UUID:
        pass

    @abstractmethod
    def CreateMFASession(
        self,
        userId: UUID,
        clientId: UUID,
        scopes: List[str],
        codeChallenge: str,
        authenticationCodeId: Optional[UUID],
    ) -> UUID:
        pass

    @abstractmethod
    def ValidateSession(
        self,
        sessionId: str,
        requiredScopes: List[str],
        clientId: str,
        codeChallenge: str,
        authenticationMethod: AuthenticationMethod,
    ) -> None:
        pass
