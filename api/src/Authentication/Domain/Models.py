import re
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID
from pydantic import BaseModel, Field
from src.Shared.Events.Models import EventEmitter


class HistoryClass(BaseModel):
    createdAt: datetime = datetime.now(timezone.utc)
    updatedAt: datetime = datetime.now(timezone.utc)

    @staticmethod
    def UpdateTimestamp(func):
        """
        Decorator to update the updatedAt timestamp on method calls.
        """

        def Wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self.updatedAt = datetime.now(timezone.utc)
            return result

        return Wrapper


class AuthenticationCredentials(HistoryClass, EventEmitter):
    id: UUID = Field(default_factory=UUID)
    userId: UUID = Field(default_factory=UUID)
    username: str = Field(..., min_length=3, max_length=50)
    passwordHash: str = Field(...)
    mfaEnabled: bool = False
    mfaSecret: Optional[str] = None

    @classmethod
    def Create(
        cls,
        id: UUID,
        userId: UUID,
        username: str,
        passwordHash: str,
        mfaEnabled: bool = False,
        mfaSecret: Optional[str] = None,
    ) -> "AuthenticationCredentials":
        """
        Factory method to create a new AuthenticationCredentials instance.
        """

        now = datetime.now(timezone.utc)
        authenticationCredentials = cls(
            id=id,
            userId=userId,
            username=username,
            passwordHash=passwordHash,
            mfaEnabled=mfaEnabled,
            mfaSecret=mfaSecret,
            createdAt=now,
            updatedAt=now,
        )

        # Emit event for creation if needed
        # authenticationCredentials.EmitEvent(
        # AuthenticationCreated.FromModel(authenticationCredentials)
        # )

        return authenticationCredentials

    @classmethod
    def FromDatabase(cls, data: dict) -> "AuthenticationCredentials":
        """
        Factory method to create an AuthenticationCredentials instance from database data.
        """

        return cls(
            id=UUID(data["id"]),
            userId=UUID(data["userId"]),
            username=data["username"],
            passwordHash=data["passwordHash"],
            mfaEnabled=data["mfaEnabled"],
            mfaSecret=data.get("mfaSecret"),
            createdAt=datetime.fromisoformat(data["createdAt"]),
            updatedAt=datetime.fromisoformat(data["updatedAt"]),
        )

    def ToDict(self) -> dict:
        """
        Serialize the AuthenticationCredentials instance to a dictionary.
        """

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

    @HistoryClass.UpdateTimestamp
    def ChangePassword(self, newPasswordHash: str) -> None:
        """
        Change the password hash and emit a PasswordChanged event.
        """

        # oldPasswordHash = self.passwordHash
        self.passwordHash = newPasswordHash
        # Emit event for password change
        # self.EmitEvent(PasswordChanged.FromModel(oldPasswordHash, self))

    @HistoryClass.UpdateTimestamp
    def EnableMFA(self, mfaSecret: str) -> None:
        """
        Enable MFA and set the MFA secret; emit an MFAEnabled event.
        """
        if self.mfaEnabled:
            return

        self.mfaEnabled = True
        self.mfaSecret = mfaSecret
        # Emit event for enabling MFA
        # self.EmitEvent(MFAEnabled.FromModel(self))

    @HistoryClass.UpdateTimestamp
    def DisableMFA(self) -> None:
        """
        Disable MFA and clear the MFA secret; emit an MFADisabled event.
        """

        self.mfaEnabled = False
        self.mfaSecret = None
        # Emit event for disabling MFA
        # self.EmitEvent(MFADisabled.FromModel(self))


class Role(HistoryClass, EventEmitter):
    id: UUID = Field(default_factory=UUID)
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None

    @classmethod
    def Create(
        cls,
        id: UUID,
        name: str,
        description: Optional[str] = None,
    ) -> "Role":
        """
        Factory method to create a new Role instance.
        """

        now = datetime.now(timezone.utc)
        role = cls(
            id=id,
            name=name,
            description=description,
            createdAt=now,
            updatedAt=now,
        )

        # Emit event for creation if needed
        # role.EmitEvent(RoleCreated.FromModel(role))

        return role

    @classmethod
    def FromDatabase(cls, data: dict) -> "Role":
        """
        Factory method to create a Role instance from database data.
        """

        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            description=data.get("description"),
            createdAt=datetime.fromisoformat(data["createdAt"]),
            updatedAt=datetime.fromisoformat(data["updatedAt"]),
        )

    def ToDict(self) -> dict:
        """
        Serialize the Role instance to a dictionary.
        """

        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "createdAt": self.createdAt.isoformat(),
            "updatedAt": self.updatedAt.isoformat(),
        }

    @HistoryClass.UpdateTimestamp
    def ChangeDescription(self, newDescription: Optional[str]) -> None:
        """
        Change the role's description and emit a RoleDescriptionUpdated event.
        """

        self.description = newDescription
        # Emit event for updating description
        # self.EmitEvent(RoleDescriptionChanged.FromModel(self))

    @HistoryClass.UpdateTimestamp
    def ChangeName(self, newName: str) -> None:
        """
        Change the role's name and emit a RoleNameUpdated event.
        """
        if not newName or newName.isspace():
            raise ValueError("Invalid role name")

        if self.name == newName.strip():
            return

        self.name = newName.strip()
        # Emit event for updating name
        # self.EmitEvent(RoleNameChanged.FromModel(self))


class RoleAssignment(HistoryClass, EventEmitter):
    id: UUID = Field(default_factory=UUID)
    userId: UUID = Field(default_factory=UUID)
    roleId: UUID = Field(default_factory=UUID)

    @classmethod
    def Create(
        cls,
        id: UUID,
        userId: UUID,
        roleId: UUID,
    ) -> "RoleAssignment":
        """
        Factory method to create a new RoleAssignment instance.
        """

        now = datetime.now(timezone.utc)
        roleAssignment = cls(
            id=id,
            userId=userId,
            roleId=roleId,
            createdAt=now,
            updatedAt=now,
        )

        # Emit event for creation if needed
        # roleAssignment.EmitEvent(RoleAssigned.FromModel(roleAssignment))

        return roleAssignment

    @classmethod
    def FromDatabase(cls, data: dict) -> "RoleAssignment":
        """
        Factory method to create a RoleAssignment instance from database data.
        """

        return cls(
            id=UUID(data["id"]),
            userId=UUID(data["userId"]),
            roleId=UUID(data["roleId"]),
            createdAt=datetime.fromisoformat(data["createdAt"]),
            updatedAt=datetime.fromisoformat(data["updatedAt"]),
        )

    def ToDict(self) -> dict:
        """
        Serialize the RoleAssignment instance to a dictionary.
        """

        return {
            "id": str(self.id),
            "userId": str(self.userId),
            "roleId": str(self.roleId),
            "createdAt": self.createdAt.isoformat(),
            "updatedAt": self.updatedAt.isoformat(),
        }


class User(HistoryClass, EventEmitter):
    id: UUID = Field(default_factory=UUID)
    email: str = Field(..., min_length=5, max_length=100)
    isActive: bool = True
    isVerified: bool = False
    authenticationCredentials: AuthenticationCredentials
    roleAssignments: list[RoleAssignment] = Field(default_factory=list)

    @classmethod
    def Create(
        cls,
        id: UUID,
        email: str,
        authenticationCredentials: AuthenticationCredentials,
        roleAssignments: Optional[list[RoleAssignment]] = None,
        isActive: bool = True,
        isVerified: bool = False,
    ) -> "User":
        """
        Factory method to create a new User instance.
        """

        now = datetime.now(timezone.utc)
        user = cls(
            id=id,
            email=email,
            isActive=isActive,
            isVerified=isVerified,
            authenticationCredentials=authenticationCredentials,
            roleAssignments=roleAssignments or [],
            createdAt=now,
            updatedAt=now,
        )

        # Emit event for creation if needed
        # user.EmitEvent(UserCreated.FromModel(user))

        return user

    @classmethod
    def FromDatabase(cls, data: dict) -> "User":
        """
        Factory method to create a User instance from database data.
        """

        return cls(
            id=UUID(data["id"]),
            email=data["email"],
            isActive=data["isActive"],
            isVerified=data["isVerified"],
            authenticationCredentials=AuthenticationCredentials.FromDatabase(
                data["authenticationCredentials"]
            ),
            roleAssignments=[
                RoleAssignment.FromDatabase(ra) for ra in data.get("roleAssignments", [])
            ],
            createdAt=datetime.fromisoformat(data["createdAt"]),
            updatedAt=datetime.fromisoformat(data["updatedAt"]),
        )

    def ToDict(self) -> dict:
        """
        Serialize the User instance to a dictionary.
        """

        return {
            "id": str(self.id),
            "email": self.email,
            "isActive": self.isActive,
            "isVerified": self.isVerified,
            "authenticationCredentials": self.authenticationCredentials.ToDict(),
            "roleAssignments": [ra.ToDict() for ra in self.roleAssignments],
            "createdAt": self.createdAt.isoformat(),
            "updatedAt": self.updatedAt.isoformat(),
        }

    @HistoryClass.UpdateTimestamp
    def Activate(self) -> None:
        """
        Activate the user and emit a UserActivated event.
        """

        self.isActive = True
        # Emit event for activation
        # self.EmitEvent(UserActivated.FromModel(self))

    @HistoryClass.UpdateTimestamp
    def Deactivate(self) -> None:
        """
        Deactivate the user and emit a UserDeactivated event.
        """

        self.isActive = False
        # Emit event for deactivation
        # self.EmitEvent(UserDeactivated.FromModel(self))

    @HistoryClass.UpdateTimestamp
    def Verify(self) -> None:
        """
        Verify the user and emit a UserVerified event.
        """

        self.isVerified = True
        # Emit event for verification
        # self.EmitEvent(UserVerified.FromModel(self))

    @HistoryClass.UpdateTimestamp
    def Unverify(self) -> None:
        """
        Unverify the user and emit a UserUnverified event.
        """

        self.isVerified = False
        # Emit event for unverification
        # self.EmitEvent(UserUnverified.FromModel(self))

    @HistoryClass.UpdateTimestamp
    def AddRoleAssignment(self, roleAssignment: RoleAssignment) -> None:
        """
        Add a role assignment to the user and emit a RoleAssignmentAdded event.
        """

        if any(ra.id == roleAssignment.id for ra in self.roleAssignments):
            raise ValueError("Role assignment already exists for user")

        self.roleAssignments.append(roleAssignment)
        # Emit event for adding role assignment
        # self.EmitEvent(RoleAssignmentAdded.FromModel(self, roleAssignment))

    @HistoryClass.UpdateTimestamp
    def RemoveRoleAssignment(self, roleAssignmentId: UUID) -> None:
        """
        Remove a role assignment from the user and emit a RoleAssignmentRemoved event.
        """

        if not any(ra.id == roleAssignmentId for ra in self.roleAssignments):
            raise ValueError("Role assignment not found for user")

        self.roleAssignments = [ra for ra in self.roleAssignments if ra.id != roleAssignmentId]
        # Emit event for removing role assignment
        # self.EmitEvent(RoleAssignmentRemoved.FromModel(self, roleAssignmentId))

    @HistoryClass.UpdateTimestamp
    def ChangeEmail(self, newEmail: str) -> None:
        """
        Change the user's email and emit a UserEmailChanged event.
        """

        if not newEmail or newEmail.isspace():
            raise ValueError("Invalid email address")

        if self.email == newEmail:
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", newEmail):
            raise ValueError("Invalid email format")

        self.email = newEmail
        # Emit event for changing email
        # self.EmitEvent(UserEmailChanged.FromModel(self))

    @HistoryClass.UpdateTimestamp
    def ClearRoleAssignments(self) -> None:
        """
        Clear all role assignments from the user and emit a RoleAssignmentsCleared event.
        """

        self.roleAssignments = []
        # Emit event for clearing role assignments
        # self.EmitEvent(RoleAssignmentsCleared.FromModel(self))
