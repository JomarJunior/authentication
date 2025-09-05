from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (
    Session as DatabaseSession,
)
from src.Session.Domain.Interfaces import ISessionRepository
from src.Session.Domain.Models import Session
from src.Session.Infrastructure.Database.Models import SessionDatabaseModel


class SqlSessionRepository(ISessionRepository):
    def __init__(self, session: DatabaseSession):
        self.session = session

    def ListAll(
        self, sortBy: str = "createdAt", sortOrder: str = "asc", limit: int = 100, offset: int = 0
    ) -> list[Session]:
        if sortBy not in SessionDatabaseModel.__table__.columns.keys():
            sortBy = "createdAt"

        sortColumn = getattr(SessionDatabaseModel, sortBy)
        sortColumn = sortColumn.desc() if sortOrder.lower() == "desc" else sortColumn.asc()

        stmt = sa.select(SessionDatabaseModel).order_by(sortColumn).limit(limit).offset(offset)
        dbSessions = self.session.execute(stmt).scalars().all()
        return [dbSession.ToModel() for dbSession in dbSessions]

    def FindById(self, sessionId: UUID) -> Session | None:
        stmt = sa.select(SessionDatabaseModel).where(SessionDatabaseModel.id == sessionId)
        dbSession = self.session.execute(stmt).scalar_one_or_none()
        return dbSession.ToModel() if dbSession else None

    def Save(self, session: Session) -> None:
        dbSession = SessionDatabaseModel.FromModel(session)
        try:
            self.session.merge(dbSession)  # replaces update+add
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError("Session with given details already exists.") from e
        except Exception as e:
            self.session.rollback()
            raise e
