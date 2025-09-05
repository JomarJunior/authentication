from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.Authentication.Domain.Models import User


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


class IHashingService(ABC):
    @abstractmethod
    def Hash(self, plainText: str) -> str:
        pass

    @abstractmethod
    def Verify(self, plainText: str, hashed: str) -> bool:
        pass
