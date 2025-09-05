from uuid import UUID
from abc import ABC, abstractmethod
from typing import List, Optional
from src.Session.Domain.Models import Session


class ISessionRepository(ABC):
    @abstractmethod
    def ListAll(self, sortBy: str, sortOrder: str, limit: int, offset: int) -> List[Session]:
        pass

    @abstractmethod
    def FindById(self, sessionId: UUID) -> Optional[Session]:
        pass

    @abstractmethod
    def Save(self, session: Session) -> None:
        pass
