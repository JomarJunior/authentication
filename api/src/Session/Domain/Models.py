from uuid import UUID
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import Field
from src.Shared.Models import HistoryClass
from src.Shared.Events.Models import EventEmitter
from src.Shared.Models import AuthenticationMethod


# Being a HistoryClass, it is also a pydantic BaseModel
class Session(HistoryClass, EventEmitter):
    id: UUID = Field(...)
    userId: UUID = Field(...)
    clientId: UUID = Field(...)
    scopes: List[str] = Field(default_factory=list)
    codeChallenge: str = Field(min_length=43, max_length=128)
    expiresAt: Optional[datetime] = Field(default=None)
    authenticationMethod: AuthenticationMethod = Field(...)
    authenticationCodeId: Optional[UUID] = Field(default=None)

    @classmethod
    def Create(
        cls,
        id: UUID,
        userId: UUID,
        clientId: UUID,
        scopes: List[str],
        codeChallenge: str,
        authenticationMethod: AuthenticationMethod,
        authenticationCodeId: Optional[UUID],
    ) -> "Session":
        session = cls(
            id=id,
            userId=userId,
            clientId=clientId,
            scopes=scopes,
            codeChallenge=codeChallenge,
            authenticationMethod=authenticationMethod,
            authenticationCodeId=authenticationCodeId,
        )

        # Emit event if needed, e.g., SessionCreated
        # session.EmitEvent(SessionCreated.FromModel(session))
        return session

    @classmethod
    def FromDatabase(cls, data: Dict[str, Any]) -> "Session":
        return cls(
            id=data["id"],
            userId=data["userId"],
            clientId=data["clientId"],
            scopes=data.get("scopes", []),
            codeChallenge=data["codeChallenge"],
            authenticationMethod=AuthenticationMethod(value=data["authenticationMethod"]),
            authenticationCodeId=data.get("authenticationCodeId"),
            expiresAt=data.get("expiresAt"),
            createdAt=datetime.fromisoformat(data["createdAt"]),
            updatedAt=datetime.fromisoformat(data["updatedAt"]),
        )

    def ToDict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "userId": str(self.userId),
            "clientId": str(self.clientId),
            "scopes": self.scopes,
            "codeChallenge": self.codeChallenge,
            "authenticationMethod": str(self.authenticationMethod),
            "authenticationCodeId": (
                str(self.authenticationCodeId) if self.authenticationCodeId else None
            ),
            "expiresAt": self.expiresAt.isoformat() if self.expiresAt else None,
            "createdAt": self.createdAt.isoformat(),
            "updatedAt": self.updatedAt.isoformat(),
        }

    @classmethod
    def ToDicts(cls, sessions: List["Session"]) -> List[Dict[str, Any]]:
        return [session.ToDict() for session in sessions]

    @HistoryClass.UpdateTimestamp
    def Revoke(self):
        self.expiresAt = datetime.now(tz=timezone.utc)
        # Emit event if needed, e.g., SessionRevoked
        # self.EmitEvent(SessionRevoked.FromModel(self))

    @HistoryClass.UpdateTimestamp
    def RevokeAt(self, expiresAt: datetime):
        self.expiresAt = expiresAt
        # Emit event if needed, e.g., SessionRevoked
        # self.EmitEvent(SessionRevoked.FromModel(self))

    def IsActive(self) -> bool:
        if self.expiresAt is None:
            return True
        return self.expiresAt > datetime.now(tz=timezone.utc)

    def HasScope(self, scope: str) -> bool:
        return scope in self.scopes

    def HasAllScopes(self, requiredScopes: List[str]) -> bool:
        return all(scope in self.scopes for scope in requiredScopes)
