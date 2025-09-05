from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
import sqlalchemy as sa
from src.Session.Domain.Models import Session

Base = declarative_base()


class SessionDatabaseModel(Base):
    __tablename__ = "t_sessions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")
    )
    userId: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True))
    clientId: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True))
    scopes: Mapped[list[str]] = mapped_column(sa.ARRAY(sa.String), default=[])
    codeChallenge: Mapped[str] = mapped_column(sa.String, nullable=False)
    expiresAt: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    authenticationMethod: Mapped[str] = mapped_column(sa.String, nullable=False)
    authenticationCodeId: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    createdAt: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )
    updatedAt: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )

    @classmethod
    def FromModel(cls, model: Session):
        return cls(
            id=model.id,
            userId=model.userId,
            clientId=model.clientId,
            scopes=model.scopes,
            codeChallenge=model.codeChallenge,
            expiresAt=model.expiresAt,
            authenticationMethod=str(model.authenticationMethod),
            authenticationCodeId=model.authenticationCodeId,
            createdAt=model.createdAt,
            updatedAt=model.updatedAt,
        )

    def ToModel(self) -> Session:
        return Session.FromDatabase(self.ToDict())

    def ToDict(self) -> dict:
        return {
            "id": str(self.id),
            "userId": str(self.userId),
            "clientId": str(self.clientId),
            "scopes": self.scopes,
            "codeChallenge": self.codeChallenge,
            "authenticationMethod": self.authenticationMethod,
            "authenticationCodeId": (
                str(self.authenticationCodeId) if self.authenticationCodeId else None
            ),
            "expiresAt": self.expiresAt.isoformat() if self.expiresAt else None,
            "createdAt": self.createdAt.isoformat(),
            "updatedAt": self.updatedAt.isoformat(),
        }
