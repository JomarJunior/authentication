"""
Unit tests for ListAllUsers Command and Handler classes.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pydantic import ValidationError
from src.Authentication.Application.ListAllUsers import (
    ListAllUsersCommand as Command,
    ListAllUsersHandler as Handler,
)
from src.Authentication.Domain.Models import User
from src.Authentication.Domain.Interfaces import IUserRepository
from src.Shared.Logging.Interfaces import ILogger


class TestCommand:
    """Test cases for ListAllUsers Command class."""

    def test_init_with_default_values(self):
        """Test Command initialization with default values."""
        command = Command()

        assert command.sortBy == "id"
        assert command.sortOrder == "asc"
        assert command.limit == 10
        assert command.offset == 0

    def test_init_with_custom_values(self):
        """Test Command initialization with custom values."""
        command = Command(sortBy="email", sortOrder="desc", limit=50, offset=20)

        assert command.sortBy == "email"
        assert command.sortOrder == "desc"
        assert command.limit == 50
        assert command.offset == 20

    def test_init_with_all_allowed_sort_fields(self):
        """Test Command initialization with all allowed sort fields."""
        allowed_fields = ["id", "email", "username", "createdAt", "updatedAt"]

        for field in allowed_fields:
            command = Command(sortBy=field)
            assert command.sortBy == field

    def test_init_with_both_sort_orders(self):
        """Test Command initialization with both allowed sort orders."""
        for order in ["asc", "desc"]:
            command = Command(sortOrder=order)
            assert command.sortOrder == order

    def test_init_with_limit_boundary_values(self):
        """Test Command initialization with limit boundary values."""
        # Minimum allowed limit
        command_min = Command(limit=1)
        assert command_min.limit == 1

        # Maximum allowed limit
        command_max = Command(limit=100)
        assert command_max.limit == 100

    def test_init_with_zero_offset(self):
        """Test Command initialization with zero offset."""
        command = Command(offset=0)
        assert command.offset == 0

    def test_init_with_large_offset(self):
        """Test Command initialization with large offset."""
        command = Command(offset=1000)
        assert command.offset == 1000

    def test_invalid_sort_by_field(self):
        """Test Command validation with invalid sortBy field."""
        with pytest.raises(ValidationError) as exc_info:
            Command(sortBy="invalid_field")

        assert "sortBy must be one of" in str(exc_info.value)

    def test_invalid_sort_order(self):
        """Test Command validation with invalid sortOrder."""
        with pytest.raises(ValidationError) as exc_info:
            Command(sortOrder="invalid_order")

        assert "sortOrder must be one of" in str(exc_info.value)

    def test_limit_below_minimum(self):
        """Test Command validation with limit below minimum."""
        with pytest.raises(ValidationError):
            Command(limit=0)

    def test_limit_above_maximum(self):
        """Test Command validation with limit above maximum."""
        with pytest.raises(ValidationError):
            Command(limit=101)

    def test_negative_offset(self):
        """Test Command validation with negative offset."""
        with pytest.raises(ValidationError):
            Command(offset=-1)

    def test_case_sensitive_sort_by_validation(self):
        """Test that sortBy validation is case sensitive."""
        with pytest.raises(ValidationError):
            Command(sortBy="ID")  # Should be "id"

        with pytest.raises(ValidationError):
            Command(sortBy="Email")  # Should be "email"

    def test_case_sensitive_sort_order_validation(self):
        """Test that sortOrder validation is case sensitive."""
        with pytest.raises(ValidationError):
            Command(sortOrder="ASC")  # Should be "asc"

        with pytest.raises(ValidationError):
            Command(sortOrder="DESC")  # Should be "desc"

    def test_validate_sort_by_classmethod(self):
        """Test ValidateSortBy class method directly."""
        # Valid values should pass
        for valid_value in ["id", "email", "username", "createdAt", "updatedAt"]:
            result = Command.ValidateSortBy(valid_value)
            assert result == valid_value

        # Invalid values should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            Command.ValidateSortBy("invalid")
        assert "sortBy must be one of" in str(exc_info.value)

    def test_validate_sort_order_classmethod(self):
        """Test ValidateSortOrder class method directly."""
        # Valid values should pass
        for valid_value in ["asc", "desc"]:
            result = Command.ValidateSortOrder(valid_value)
            assert result == valid_value

        # Invalid values should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            Command.ValidateSortOrder("invalid")
        assert "sortOrder must be one of" in str(exc_info.value)

    def test_field_constraints_types(self):
        """Test that fields have correct types."""
        command = Command()

        assert isinstance(command.sortBy, str)
        assert isinstance(command.sortOrder, str)
        assert isinstance(command.limit, int)
        assert isinstance(command.offset, int)

    def test_pydantic_serialization(self):
        """Test that Command can be serialized properly."""
        command = Command(sortBy="email", sortOrder="desc", limit=25, offset=50)

        # Test model_dump
        data = command.model_dump()
        expected = {"sortBy": "email", "sortOrder": "desc", "limit": 25, "offset": 50}
        assert data == expected

    def test_pydantic_deserialization(self):
        """Test that Command can be deserialized from dict."""
        data = {"sortBy": "username", "sortOrder": "asc", "limit": 15, "offset": 5}

        command = Command(**data)
        assert command.sortBy == "username"
        assert command.sortOrder == "asc"
        assert command.limit == 15
        assert command.offset == 5


class TestHandler:
    """Test cases for ListAllUsers Handler class."""

    @pytest.fixture
    def mock_user_repository(self):
        """Create a mock user repository."""
        return Mock(spec=IUserRepository)

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger."""
        return Mock(spec=ILogger)

    @pytest.fixture
    def handler(self, mock_user_repository, mock_logger):
        """Create a Handler instance with mocked dependencies."""
        return Handler(mock_user_repository, mock_logger)

    @pytest.fixture
    def sample_users(self):
        """Create sample User objects for testing."""
        # Create mock users that have ToDict method
        user1 = Mock(spec=User)
        user1.ToDict.return_value = {
            "id": "user1-id",
            "email": "user1@example.com",
            "username": "user1",
        }

        user2 = Mock(spec=User)
        user2.ToDict.return_value = {
            "id": "user2-id",
            "email": "user2@example.com",
            "username": "user2",
        }

        return [user1, user2]

    def test_init(self, mock_user_repository, mock_logger):
        """Test Handler initialization."""
        handler = Handler(mock_user_repository, mock_logger)

        assert handler.userRepository is mock_user_repository
        assert handler.logger is mock_logger

    def test_handle_with_default_command(
        self, handler, mock_user_repository, mock_logger, sample_users
    ):
        """Test Handle method with default command values."""
        command = Command()
        mock_user_repository.ListAll.return_value = sample_users

        # Mock the User.ToDicts static method
        with patch.object(User, "ToDicts") as mock_to_dicts:
            expected_result = [user.ToDict() for user in sample_users]
            mock_to_dicts.return_value = expected_result

            result = handler.Handle(command)

            # Verify repository was called with correct parameters
            mock_user_repository.ListAll.assert_called_once_with(
                sortBy="id", sortOrder="asc", limit=10, offset=0
            )

            # Verify logging calls
            assert mock_logger.Info.call_count == 2
            mock_logger.Info.assert_any_call(
                f"""Listing users sorted by id in 
            asc order, limit 10, offset 0"""
            )
            mock_logger.Info.assert_any_call("Listed 2 users")

            # Verify User.ToDicts was called with the users
            mock_to_dicts.assert_called_once_with(sample_users)

            # Verify result
            assert result == expected_result

    def test_handle_with_custom_command(
        self, handler, mock_user_repository, mock_logger, sample_users
    ):
        """Test Handle method with custom command values."""
        command = Command(sortBy="email", sortOrder="desc", limit=50, offset=20)
        mock_user_repository.ListAll.return_value = sample_users

        with patch.object(User, "ToDicts") as mock_to_dicts:
            expected_result = [user.ToDict() for user in sample_users]
            mock_to_dicts.return_value = expected_result

            result = handler.Handle(command)

            # Verify repository was called with correct parameters
            mock_user_repository.ListAll.assert_called_once_with(
                sortBy="email", sortOrder="desc", limit=50, offset=20
            )

            # Verify logging calls
            assert mock_logger.Info.call_count == 2
            mock_logger.Info.assert_any_call(
                f"""Listing users sorted by email in 
            desc order, limit 50, offset 20"""
            )
            mock_logger.Info.assert_any_call("Listed 2 users")

            # Verify result
            assert result == expected_result

    def test_handle_with_empty_user_list(self, handler, mock_user_repository, mock_logger):
        """Test Handle method when repository returns empty list."""
        command = Command()
        mock_user_repository.ListAll.return_value = []

        with patch.object(User, "ToDicts") as mock_to_dicts:
            mock_to_dicts.return_value = []

            result = handler.Handle(command)

            # Verify repository was called
            mock_user_repository.ListAll.assert_called_once()

            # Verify logging shows 0 users
            mock_logger.Info.assert_any_call("Listed 0 users")

            # Verify empty result
            assert result == []

    def test_handle_with_single_user(self, handler, mock_user_repository, mock_logger):
        """Test Handle method with single user result."""
        command = Command()
        single_user = Mock(spec=User)
        single_user.ToDict.return_value = {"id": "single-user", "email": "single@example.com"}
        mock_user_repository.ListAll.return_value = [single_user]

        with patch.object(User, "ToDicts") as mock_to_dicts:
            expected_result = [single_user.ToDict()]
            mock_to_dicts.return_value = expected_result

            result = handler.Handle(command)

            # Verify logging shows 1 user
            mock_logger.Info.assert_any_call("Listed 1 users")

            # Verify result
            assert result == expected_result

    def test_handle_with_all_sort_fields(
        self, handler, mock_user_repository, mock_logger, sample_users
    ):
        """Test Handle method with all allowed sort fields."""
        allowed_fields = ["id", "email", "username", "createdAt", "updatedAt"]

        for sort_field in allowed_fields:
            mock_user_repository.reset_mock()
            mock_logger.reset_mock()

            command = Command(sortBy=sort_field)
            mock_user_repository.ListAll.return_value = sample_users

            with patch.object(User, "ToDicts") as mock_to_dicts:
                mock_to_dicts.return_value = []

                handler.Handle(command)

                # Verify repository was called with correct sortBy
                mock_user_repository.ListAll.assert_called_once_with(
                    sortBy=sort_field, sortOrder="asc", limit=10, offset=0
                )

    def test_handle_with_both_sort_orders(
        self, handler, mock_user_repository, mock_logger, sample_users
    ):
        """Test Handle method with both sort orders."""
        for sort_order in ["asc", "desc"]:
            mock_user_repository.reset_mock()
            mock_logger.reset_mock()

            command = Command(sortOrder=sort_order)
            mock_user_repository.ListAll.return_value = sample_users

            with patch.object(User, "ToDicts") as mock_to_dicts:
                mock_to_dicts.return_value = []

                handler.Handle(command)

                # Verify repository was called with correct sortOrder
                mock_user_repository.ListAll.assert_called_once_with(
                    sortBy="id", sortOrder=sort_order, limit=10, offset=0
                )

    def test_handle_with_boundary_limit_values(
        self, handler, mock_user_repository, mock_logger, sample_users
    ):
        """Test Handle method with boundary limit values."""
        for limit_value in [1, 100]:
            mock_user_repository.reset_mock()
            mock_logger.reset_mock()

            command = Command(limit=limit_value)
            mock_user_repository.ListAll.return_value = sample_users

            with patch.object(User, "ToDicts") as mock_to_dicts:
                mock_to_dicts.return_value = []

                handler.Handle(command)

                # Verify repository was called with correct limit
                mock_user_repository.ListAll.assert_called_once_with(
                    sortBy="id", sortOrder="asc", limit=limit_value, offset=0
                )

    def test_handle_with_large_offset(
        self, handler, mock_user_repository, mock_logger, sample_users
    ):
        """Test Handle method with large offset value."""
        command = Command(offset=1000)
        mock_user_repository.ListAll.return_value = sample_users

        with patch.object(User, "ToDicts") as mock_to_dicts:
            mock_to_dicts.return_value = []

            handler.Handle(command)

            # Verify repository was called with correct offset
            mock_user_repository.ListAll.assert_called_once_with(
                sortBy="id", sortOrder="asc", limit=10, offset=1000
            )

    def test_handle_logging_message_format(
        self, handler, mock_user_repository, mock_logger, sample_users
    ):
        """Test that logging messages have correct format."""
        command = Command(sortBy="username", sortOrder="desc", limit=25, offset=5)
        mock_user_repository.ListAll.return_value = sample_users

        with patch.object(User, "ToDicts") as mock_to_dicts:
            mock_to_dicts.return_value = []

            handler.Handle(command)

            # Check the exact logging message format
            expected_first_message = f"""Listing users sorted by username in 
            desc order, limit 25, offset 5"""
            mock_logger.Info.assert_any_call(expected_first_message)
            mock_logger.Info.assert_any_call("Listed 2 users")

    def test_handle_preserves_user_data_integrity(self, handler, mock_user_repository, mock_logger):
        """Test that Handle method preserves user data integrity."""
        command = Command()

        # Create users with specific data
        user1 = Mock(spec=User)
        user1.ToDict.return_value = {
            "id": "123",
            "email": "test@example.com",
            "username": "testuser",
            "createdAt": "2024-01-01T00:00:00Z",
        }

        user2 = Mock(spec=User)
        user2.ToDict.return_value = {
            "id": "456",
            "email": "another@example.com",
            "username": "anotheruser",
            "createdAt": "2024-01-02T00:00:00Z",
        }

        users = [user1, user2]
        mock_user_repository.ListAll.return_value = users

        with patch.object(User, "ToDicts") as mock_to_dicts:
            expected_result = [user.ToDict() for user in users]
            mock_to_dicts.return_value = expected_result

            result = handler.Handle(command)

            # Verify that the exact user data is preserved
            assert len(result) == 2
            assert result == expected_result

            # Verify User.ToDicts was called with original users
            mock_to_dicts.assert_called_once_with(users)

    def test_handle_error_propagation(self, handler, mock_user_repository, mock_logger):
        """Test that Handle method properly propagates repository errors."""
        command = Command()

        # Make repository raise an exception
        mock_user_repository.ListAll.side_effect = Exception("Database error")

        # Verify exception is propagated
        with pytest.raises(Exception, match="Database error"):
            handler.Handle(command)

        # Verify first log was called before error
        mock_logger.Info.assert_called_once_with(
            f"""Listing users sorted by id in 
            asc order, limit 10, offset 0"""
        )

    def test_handler_dependency_injection(self):
        """Test that Handler properly uses dependency injection."""
        # Create specific mock instances
        repo_mock = Mock(spec=IUserRepository)
        logger_mock = Mock(spec=ILogger)

        # Create handler with these dependencies
        handler = Handler(repo_mock, logger_mock)

        # Verify dependencies are stored correctly
        assert handler.userRepository is repo_mock
        assert handler.logger is logger_mock

        # Verify they are different instances
        assert handler.userRepository is not Mock(spec=IUserRepository)
        assert handler.logger is not Mock(spec=ILogger)
