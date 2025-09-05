from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (
    Session as DatabaseSession,
    joinedload,
)
from src.Authentication.Domain.Interfaces import IUserRepository, IAuthCodeRepository
from src.Authentication.Domain.Models import AuthenticationCode, User
from src.Authentication.Infrastructure.Database.Models import (
    UserDatabaseModel,
    AuthenticationCredentialsDatabaseModel,
    AuthenticationCodeDatabaseModel,
)


class SqlUserRepository(IUserRepository):
    def __init__(self, session: DatabaseSession):
        self.session = session

    def FindById(self, id: UUID) -> User | None:
        stmt = (
            sa.select(UserDatabaseModel)
            .options(
                joinedload(UserDatabaseModel.authenticationCredentials),
                joinedload(UserDatabaseModel.roleAssignments),
            )
            .where(UserDatabaseModel.id == id)
        )
        dbUser = self.session.execute(stmt).unique().scalar_one_or_none()
        return dbUser.ToModel() if dbUser else None

    def FindByEmail(self, email: str) -> User | None:
        stmt = (
            sa.select(UserDatabaseModel)
            .options(
                joinedload(UserDatabaseModel.authenticationCredentials),
                joinedload(UserDatabaseModel.roleAssignments),
            )
            .where(UserDatabaseModel.email == email)
        )
        dbUser = self.session.execute(stmt).unique().scalar_one_or_none()
        return dbUser.ToModel() if dbUser else None

    def FindByUsername(self, username: str) -> User | None:
        stmt = (
            sa.select(UserDatabaseModel)
            .options(
                joinedload(UserDatabaseModel.authenticationCredentials),
                joinedload(UserDatabaseModel.roleAssignments),
            )
            .join(UserDatabaseModel.authenticationCredentials)
            .where(AuthenticationCredentialsDatabaseModel.username == username)
        )
        dbUser = self.session.execute(stmt).unique().scalar_one_or_none()
        return dbUser.ToModel() if dbUser else None

    def ListAll(
        self, sortBy: str = "email", sortOrder: str = "asc", limit: int = 100, offset: int = 0
    ) -> list[User]:
        if sortBy not in UserDatabaseModel.__table__.columns.keys():
            sortBy = "email"

        sortColumn = getattr(UserDatabaseModel, sortBy)
        sortColumn = sortColumn.desc() if sortOrder.lower() == "desc" else sortColumn.asc()

        stmt = (
            sa.select(UserDatabaseModel)
            .options(
                joinedload(UserDatabaseModel.authenticationCredentials),
                joinedload(UserDatabaseModel.roleAssignments),
            )
            .order_by(sortColumn)
            .limit(limit)
            .offset(offset)
        )
        dbUsers = self.session.execute(stmt).scalars().unique().all()
        return [dbUser.ToModel() for dbUser in dbUsers]

    def Save(self, user: User) -> None:
        dbUser = UserDatabaseModel.FromModel(user)
        try:
            self.session.merge(dbUser)  # replaces update+add
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError("User with given email or username already exists.") from e
        except Exception as e:
            self.session.rollback()
            raise e


class SqlAuthCodeRepository(IAuthCodeRepository):
    def __init__(self, session: DatabaseSession):
        self.session = session

    def FindByCode(self, code: str) -> AuthenticationCode | None:
        stmt = sa.select(AuthenticationCodeDatabaseModel).where(
            AuthenticationCodeDatabaseModel.code == code
        )
        dbCode = self.session.execute(stmt).unique().scalar_one_or_none()
        return dbCode.ToModel() if dbCode else None

    def Save(self, authenticationCode: AuthenticationCode) -> None:
        dbCode = AuthenticationCodeDatabaseModel.FromModel(authenticationCode)
        try:
            self.session.merge(dbCode)
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError("Authentication code already exists.") from e
        except Exception as e:
            self.session.rollback()
            raise e
