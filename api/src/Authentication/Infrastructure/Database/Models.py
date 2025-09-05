from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
import sqlalchemy as sa

from src.Authentication.Domain.Models import User, AuthenticationCredentials, RoleAssignment, Role

Base = declarative_base()


class AuthenticationCredentialsDatabaseModel(Base):
    __tablename__ = "t_authentication_credentials"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")
    )
    userId: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), sa.ForeignKey("t_users.id"))
    username: Mapped[str] = mapped_column(sa.String, unique=True, nullable=False)
    passwordHash: Mapped[str] = mapped_column(sa.String, nullable=False)
    mfaEnabled: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    mfaSecret: Mapped[str] = mapped_column(sa.String, nullable=True)
    createdAt: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )
    updatedAt: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )

    @classmethod
    def FromModel(cls, model: AuthenticationCredentials):
        return cls(
            id=model.id,
            userId=model.userId,
            username=model.username,
            passwordHash=model.passwordHash,
            mfaEnabled=model.mfaEnabled,
            mfaSecret=model.mfaSecret,
            createdAt=model.createdAt,
            updatedAt=model.updatedAt,
        )

    def ToModel(self) -> AuthenticationCredentials:
        return AuthenticationCredentials.FromDatabase(self.ToDict())

    def ToDict(self) -> dict:
        return {
            "id": str(self.id),
            "userId": str(self.userId),
            "username": self.username,
            "passwordHash": self.passwordHash,
            "mfaEnabled": self.mfaEnabled,
            "mfaSecret": self.mfaSecret,
            "createdAt": self.createdAt.isoformat(),
            "updatedAt": self.updatedAt.isoformat(),
        }


class RoleDatabaseModel(Base):
    __tablename__ = "t_roles"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(sa.String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(sa.String, nullable=True)
    createdAt: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )
    updatedAt: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )

    @classmethod
    def FromModel(cls, model: Role):
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
            createdAt=model.createdAt,
            updatedAt=model.updatedAt,
        )

    def ToModel(self) -> Role:
        return Role.FromDatabase(self.ToDict())

    def ToDict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "createdAt": self.createdAt.isoformat(),
            "updatedAt": self.updatedAt.isoformat(),
        }


class RoleAssignmentDatabaseModel(Base):
    __tablename__ = "t_role_assignments"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")
    )
    userId: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), sa.ForeignKey("t_users.id"))
    roleId: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), sa.ForeignKey("t_roles.id"))
    createdAt: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )
    updatedAt: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )

    @classmethod
    def FromModel(cls, model: RoleAssignment):
        return cls(
            id=model.id,
            userId=model.userId,
            roleId=model.roleId,
            createdAt=model.createdAt,
            updatedAt=model.updatedAt,
        )

    def ToModel(self) -> RoleAssignment:
        return RoleAssignment.FromDatabase(self.ToDict())

    def ToDict(self) -> dict:
        return {
            "id": str(self.id),
            "userId": str(self.userId),
            "roleId": str(self.roleId),
            "createdAt": self.createdAt.isoformat(),
            "updatedAt": self.updatedAt.isoformat(),
        }


class UserDatabaseModel(Base):
    __tablename__ = "t_users"

    id = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")
    )
    email = mapped_column(sa.String, unique=True, nullable=False)
    isActive = mapped_column(sa.Boolean, default=True)
    isVerified = mapped_column(sa.Boolean, default=False)
    createdAt = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )
    updatedAt = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )

    authenticationCredentials = relationship(
        "AuthenticationCredentialsDatabaseModel", uselist=False, lazy="joined"
    )
    roleAssignments = relationship("RoleAssignmentDatabaseModel", lazy="joined")

    @classmethod
    def FromModel(cls, model: User):
        return cls(
            id=model.id,
            email=model.email,
            isActive=model.isActive,
            isVerified=model.isVerified,
            createdAt=model.createdAt,
            updatedAt=model.updatedAt,
            authenticationCredentials=AuthenticationCredentialsDatabaseModel.FromModel(
                model.authenticationCredentials
            ),
            roleAssignments=[
                RoleAssignmentDatabaseModel.FromModel(ra) for ra in model.roleAssignments
            ],
        )

    def ToModel(self) -> User:
        return User.FromDatabase(self.ToDict())

    def ToDict(self) -> dict:
        return {
            "id": str(self.id),
            "email": self.email,
            "isActive": self.isActive,
            "isVerified": self.isVerified,
            "createdAt": self.createdAt.isoformat(),
            "updatedAt": self.updatedAt.isoformat(),
            "authenticationCredentials": self.authenticationCredentials.ToDict(),
            "roleAssignments": [ra.ToDict() for ra in self.roleAssignments],
        }
