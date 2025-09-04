import pytest
from uuid import UUID
from datetime import datetime
from src.Authentication.Domain.Models import AuthenticationCredentials, Role, RoleAssignment, User


class TestAuthenticationCredentials:
    @pytest.fixture
    def valid_data_mfa_enabled(self):
        return {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "userId": "123e4567-e89b-12d3-a456-426614174001",
            "username": "testuser",
            "passwordHash": "hashed_password",
            "mfaEnabled": True,
            "mfaSecret": "mfa_secret",
        }

    @pytest.fixture
    def valid_data_mfa_disabled(self):
        return {
            "id": "123e4567-e89b-12d3-a456-426614174002",
            "userId": "123e4567-e89b-12d3-a456-426614174003",
            "username": "testuser2",
            "passwordHash": "hashed_password2",
            "mfaEnabled": False,
            "mfaSecret": None,
        }

    @pytest.fixture
    def valid_database_data(self):
        return {
            "id": "123e4567-e89b-12d3-a456-426614174004",
            "userId": "123e4567-e89b-12d3-a456-426614174005",
            "username": "dbuser",
            "passwordHash": "db_hashed_password",
            "mfaEnabled": True,
            "mfaSecret": "db_mfa_secret",
            "createdAt": "2024-01-01T12:00:00",
            "updatedAt": "2024-01-02T12:00:00",
        }

    def test_create_with_mfa_enabled(self, valid_data_mfa_enabled):
        creds = AuthenticationCredentials.Create(**valid_data_mfa_enabled)
        assert creds.id == UUID(valid_data_mfa_enabled["id"])
        assert creds.userId == UUID(valid_data_mfa_enabled["userId"])
        assert creds.username == valid_data_mfa_enabled["username"]
        assert creds.passwordHash == valid_data_mfa_enabled["passwordHash"]
        assert creds.mfaEnabled is True
        assert creds.mfaSecret == valid_data_mfa_enabled["mfaSecret"]

    def test_create_with_mfa_disabled(self, valid_data_mfa_disabled):
        creds = AuthenticationCredentials.Create(**valid_data_mfa_disabled)
        assert creds.id == UUID(valid_data_mfa_disabled["id"])
        assert creds.userId == UUID(valid_data_mfa_disabled["userId"])
        assert creds.username == valid_data_mfa_disabled["username"]
        assert creds.passwordHash == valid_data_mfa_disabled["passwordHash"]
        assert creds.mfaEnabled is False
        assert creds.mfaSecret == valid_data_mfa_disabled["mfaSecret"]

    def test_create_from_database(self, valid_database_data):
        creds = AuthenticationCredentials.FromDatabase(valid_database_data)
        assert creds.id == UUID(valid_database_data["id"])
        assert creds.userId == UUID(valid_database_data["userId"])
        assert creds.username == valid_database_data["username"]
        assert creds.passwordHash == valid_database_data["passwordHash"]
        assert creds.mfaEnabled is True
        assert creds.mfaSecret == valid_database_data["mfaSecret"]
        assert creds.createdAt == datetime.fromisoformat(valid_database_data["createdAt"])
        assert creds.updatedAt == datetime.fromisoformat(valid_database_data["updatedAt"])

    def test_to_dict(self, valid_database_data):
        creds = AuthenticationCredentials.FromDatabase(valid_database_data)
        creds_dict = creds.ToDict()
        assert creds_dict == valid_database_data

    def test_change_password(self, valid_data_mfa_enabled):
        creds = AuthenticationCredentials.Create(**valid_data_mfa_enabled)
        new_password_hash = "new_hashed_password"
        creds.ChangePassword(new_password_hash)
        assert creds.passwordHash == new_password_hash

    def test_enable_mfa(self, valid_data_mfa_disabled):
        creds = AuthenticationCredentials.Create(**valid_data_mfa_disabled)
        creds.EnableMFA(mfaSecret="new_mfa_secret")
        assert creds.mfaEnabled is True
        assert creds.mfaSecret == "new_mfa_secret"

    def test_enable_mfa_when_already_enabled(self, valid_data_mfa_enabled):
        creds = AuthenticationCredentials.Create(**valid_data_mfa_enabled)
        existing_secret = creds.mfaSecret
        creds.EnableMFA(mfaSecret="another_mfa_secret")
        assert creds.mfaEnabled is True
        assert creds.mfaSecret == existing_secret

    def test_disable_mfa(self, valid_data_mfa_enabled):
        creds = AuthenticationCredentials.Create(**valid_data_mfa_enabled)
        creds.DisableMFA()
        assert creds.mfaEnabled is False
        assert creds.mfaSecret is None

    def test_disable_mfa_when_already_disabled(self, valid_data_mfa_disabled):
        creds = AuthenticationCredentials.Create(**valid_data_mfa_disabled)
        creds.DisableMFA()
        assert creds.mfaEnabled is False
        assert creds.mfaSecret is None


class TestRole:
    @pytest.fixture
    def valid_role_data(self):
        return {
            "id": "223e4567-e89b-12d3-a456-426614174000",
            "name": "admin",
            "description": "Administrator role",
        }

    @pytest.fixture
    def valid_database_role_data(self):
        return {
            "id": "223e4567-e89b-12d3-a456-426614174000",
            "name": "admin",
            "description": "Administrator role",
            "createdAt": "2024-01-01T12:00:00",
            "updatedAt": "2024-01-02T12:00:00",
        }

    def test_create_role(self, valid_role_data):
        role = Role.Create(**valid_role_data)
        assert role.id == UUID(valid_role_data["id"])
        assert role.name == valid_role_data["name"]
        assert role.description == valid_role_data["description"]

    def test_create_from_database(self, valid_database_role_data):
        role = Role.FromDatabase(valid_database_role_data)
        assert role.id == UUID(valid_database_role_data["id"])
        assert role.name == valid_database_role_data["name"]
        assert role.description == valid_database_role_data["description"]
        assert role.createdAt == datetime.fromisoformat(valid_database_role_data["createdAt"])
        assert role.updatedAt == datetime.fromisoformat(valid_database_role_data["updatedAt"])

    def test_to_dict(self, valid_database_role_data):
        role = Role.FromDatabase(valid_database_role_data)
        role_dict = role.ToDict()
        assert role_dict == valid_database_role_data

    def test_update_description(self, valid_role_data):
        role = Role.Create(**valid_role_data)
        new_description = "Changed description"
        role.ChangeDescription(new_description)
        assert role.description == new_description

    def test_update_description_to_none(self, valid_role_data):
        role = Role.Create(**valid_role_data)
        role.ChangeDescription(None)
        assert role.description is None

    def test_update_name(self, valid_role_data):
        role = Role.Create(**valid_role_data)
        new_name = "superadmin"
        role.ChangeName(new_name)
        assert role.name == new_name

    def test_update_name_to_empty_string(self, valid_role_data):
        role = Role.Create(**valid_role_data)
        with pytest.raises(ValueError):
            role.ChangeName("")

    def test_update_name_to_whitespace(self, valid_role_data):
        role = Role.Create(**valid_role_data)
        with pytest.raises(ValueError):
            role.ChangeName("   ")

    def test_update_name_to_none(self, valid_role_data):
        role = Role.Create(**valid_role_data)
        with pytest.raises(ValueError):
            role.ChangeName(None)  # type: ignore


class TestRoleAssignment:
    @pytest.fixture
    def valid_role_assignment_data(self):
        return {
            "id": "323e4567-e89b-12d3-a456-426614174000",
            "userId": "323e4567-e89b-12d3-a456-426614174001",
            "roleId": "223e4567-e89b-12d3-a456-426614174000",
        }

    @pytest.fixture
    def valid_database_role_assignment_data(self):
        return {
            "id": "323e4567-e89b-12d3-a456-426614174000",
            "userId": "323e4567-e89b-12d3-a456-426614174001",
            "roleId": "223e4567-e89b-12d3-a456-426614174000",
            "createdAt": "2024-01-01T12:00:00",
            "updatedAt": "2024-01-02T12:00:00",
        }

    def test_create_role_assignment(self, valid_role_assignment_data):
        assignment = RoleAssignment.Create(**valid_role_assignment_data)
        assert assignment.id == UUID(valid_role_assignment_data["id"])
        assert assignment.userId == UUID(valid_role_assignment_data["userId"])
        assert assignment.roleId == UUID(valid_role_assignment_data["roleId"])

    def test_create_from_database(self, valid_database_role_assignment_data):
        assignment = RoleAssignment.FromDatabase(valid_database_role_assignment_data)
        assert assignment.id == UUID(valid_database_role_assignment_data["id"])
        assert assignment.userId == UUID(valid_database_role_assignment_data["userId"])
        assert assignment.roleId == UUID(valid_database_role_assignment_data["roleId"])
        assert assignment.createdAt == datetime.fromisoformat(
            valid_database_role_assignment_data["createdAt"]
        )
        assert assignment.updatedAt == datetime.fromisoformat(
            valid_database_role_assignment_data["updatedAt"]
        )

    def test_to_dict(self, valid_database_role_assignment_data):
        assignment = RoleAssignment.FromDatabase(valid_database_role_assignment_data)
        assignment_dict = assignment.ToDict()
        assert assignment_dict == valid_database_role_assignment_data


class TestUser:
    @pytest.fixture
    def valid_user_id(self):
        return "423e4567-e89b-12d3-a456-426614174000"

    @pytest.fixture
    def valid_authentication_user_data_mfa_enabled(self):
        return {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "userId": "423e4567-e89b-12d3-a456-426614174000",
            "username": "testuser",
            "passwordHash": "hashed_password",
            "mfaEnabled": True,
            "mfaSecret": "mfa_secret",
        }

    @pytest.fixture
    def valid_authentication_user_data_mfa_disabled(self):
        return {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "userId": "423e4567-e89b-12d3-a456-426614174000",
            "username": "testuser",
            "passwordHash": "hashed_password",
            "mfaEnabled": False,
            "mfaSecret": None,
        }

    @pytest.fixture
    def valid_role_assignments_data(self, valid_user_id):
        return [
            {
                "id": "323e4567-e89b-12d3-a456-426614174000",
                "userId": valid_user_id,
                "roleId": "223e4567-e89b-12d3-a456-426614174000",
            },
            {
                "id": "323e4567-e89b-12d3-a456-426614174002",
                "userId": valid_user_id,
                "roleId": "223e4567-e89b-12d3-a456-426614174003",
            },
        ]

    @pytest.fixture
    def valid_user_data(
        self, valid_user_id, valid_authentication_user_data_mfa_enabled, valid_role_assignments_data
    ):
        return {
            "id": valid_user_id,
            "email": "john.doe@example.com",
            "isActive": True,
            "isVerified": False,
            "authenticationCredentials": AuthenticationCredentials.Create(
                **valid_authentication_user_data_mfa_enabled
            ),
            "roleAssignments": [
                RoleAssignment.Create(**data) for data in valid_role_assignments_data
            ],
        }

    @pytest.fixture
    def valid_database_user_data(self, valid_user_id):
        return {
            "id": valid_user_id,
            "email": "john.doe@example.com",
            "isActive": True,
            "isVerified": False,
            "authenticationCredentials": {
                "id": "123e4567-e89b-12d3-a456-426614174004",
                "userId": "123e4567-e89b-12d3-a456-426614174005",
                "username": "dbuser",
                "passwordHash": "db_hashed_password",
                "mfaEnabled": True,
                "mfaSecret": "db_mfa_secret",
                "createdAt": "2024-01-01T12:00:00",
                "updatedAt": "2024-01-02T12:00:00",
            },
            "roleAssignments": [
                {
                    "id": "323e4567-e89b-12d3-a456-426614174000",
                    "userId": "323e4567-e89b-12d3-a456-426614174001",
                    "roleId": "223e4567-e89b-12d3-a456-426614174000",
                    "createdAt": "2024-01-01T12:00:00",
                    "updatedAt": "2024-01-02T12:00:00",
                },
            ],
            "createdAt": "2024-01-01T12:00:00",
            "updatedAt": "2024-01-02T12:00:00",
        }

    def test_create_user(self, valid_user_data):
        user = User.Create(**valid_user_data)
        assert user.id == UUID(valid_user_data["id"])
        assert user.email == valid_user_data["email"]
        assert user.isActive == valid_user_data["isActive"]
        assert user.isVerified == valid_user_data["isVerified"]
        assert user.authenticationCredentials.id == valid_user_data["authenticationCredentials"].id
        assert len(user.roleAssignments) == len(valid_user_data["roleAssignments"])
        for ra, valid_ra in zip(user.roleAssignments, valid_user_data["roleAssignments"]):
            assert ra.id == valid_ra.id

    def test_create_from_database(self, valid_database_user_data):
        user = User.FromDatabase(valid_database_user_data)
        assert user.id == UUID(valid_database_user_data["id"])
        assert user.email == valid_database_user_data["email"]
        assert user.isActive == valid_database_user_data["isActive"]
        assert user.isVerified == valid_database_user_data["isVerified"]
        assert user.authenticationCredentials.id == UUID(
            valid_database_user_data["authenticationCredentials"]["id"]
        )
        assert len(user.roleAssignments) == len(valid_database_user_data["roleAssignments"])
        for ra, valid_ra in zip(user.roleAssignments, valid_database_user_data["roleAssignments"]):
            assert ra.id == UUID(valid_ra["id"])
        assert user.createdAt == datetime.fromisoformat(valid_database_user_data["createdAt"])
        assert user.updatedAt == datetime.fromisoformat(valid_database_user_data["updatedAt"])

    def test_to_dict(self, valid_database_user_data):
        user = User.FromDatabase(valid_database_user_data)
        user_dict = user.ToDict()
        assert user_dict == valid_database_user_data

    def test_activate(self, valid_user_data):
        user = User.Create(**valid_user_data)
        user.Activate()
        assert user.isActive is True

    def test_activate_when_already_active(self, valid_user_data):
        user = User.Create(**valid_user_data)
        user.Activate()
        assert user.isActive is True

    def test_deactivate(self, valid_user_data):
        user = User.Create(**valid_user_data)
        user.Deactivate()
        assert user.isActive is False

    def test_deactivate_when_already_inactive(self, valid_user_data):
        user = User.Create(**valid_user_data)
        user.Deactivate()
        assert user.isActive is False

    def test_verify(self, valid_user_data):
        user = User.Create(**valid_user_data)
        user.Verify()
        assert user.isVerified is True

    def test_verify_when_already_verified(self, valid_user_data):
        user = User.Create(**valid_user_data)
        user.Verify()
        assert user.isVerified is True

    def test_unverify(self, valid_user_data):
        user = User.Create(**valid_user_data)
        user.Unverify()
        assert user.isVerified is False

    def test_unverify_when_already_unverified(self, valid_user_data):
        user = User.Create(**valid_user_data)
        user.Unverify()
        assert user.isVerified is False

    def test_add_role_assignment(self, valid_user_data):
        user = User.Create(**valid_user_data)
        new_role_assignment_data = {
            "id": "323e4567-e89b-12d3-a456-426614174004",
            "userId": user.id,
            "roleId": "223e4567-e89b-12d3-a456-426614174005",
        }
        new_role_assignment = RoleAssignment.Create(**new_role_assignment_data)
        user.AddRoleAssignment(new_role_assignment)
        assert len(user.roleAssignments) == len(valid_user_data["roleAssignments"]) + 1
        assert any(ra.id == new_role_assignment.id for ra in user.roleAssignments)

    def test_add_existing_role_assignment(self, valid_user_data):
        user = User.Create(**valid_user_data)
        existing_role_assignment = user.roleAssignments[0]
        with pytest.raises(ValueError):
            user.AddRoleAssignment(existing_role_assignment)

    def test_remove_role_assignment(self, valid_user_data):
        user = User.Create(**valid_user_data)
        role_assignment_to_remove = user.roleAssignments[0]
        user.RemoveRoleAssignment(role_assignment_to_remove.id)
        assert len(user.roleAssignments) == len(valid_user_data["roleAssignments"]) - 1
        assert all(ra.id != role_assignment_to_remove.id for ra in user.roleAssignments)

    def test_remove_nonexistent_role_assignment(self, valid_user_data):
        user = User.Create(**valid_user_data)
        non_existent_id = UUID("323e4567-e89b-12d3-a456-426614174999")
        with pytest.raises(ValueError):
            user.RemoveRoleAssignment(non_existent_id)

    def test_change_email(self, valid_user_data):
        user = User.Create(**valid_user_data)
        new_email = "new_email@example.com"
        user.ChangeEmail(new_email)
        assert user.email == new_email

    def test_change_email_to_empty_string(self, valid_user_data):
        user = User.Create(**valid_user_data)
        with pytest.raises(ValueError):
            user.ChangeEmail("")

    def test_change_email_to_whitespace(self, valid_user_data):
        user = User.Create(**valid_user_data)
        with pytest.raises(ValueError):
            user.ChangeEmail("   ")

    def test_change_email_to_none(self, valid_user_data):
        user = User.Create(**valid_user_data)
        with pytest.raises(ValueError):
            user.ChangeEmail(None)  # type: ignore

    def test_change_email_to_invalid_format(self, valid_user_data):
        user = User.Create(**valid_user_data)
        with pytest.raises(ValueError):
            user.ChangeEmail("invalid-email-format")

    def test_clear_role_assignments(self, valid_user_data):
        user = User.Create(**valid_user_data)
        user.ClearRoleAssignments()
        assert len(user.roleAssignments) == 0
