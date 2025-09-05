"""
Unit tests for RegisterUser Command and Handler classes.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from uuid import UUID, uuid4
from pydantic import ValidationError
from src.Authentication.Application.RegisterUser import Command, Handler
from src.Authentication.Domain.Models import User
from src.Authentication.Domain.Interfaces import IHashingService, IUserRepository
from src.Authentication.Domain.Sevices import UniquenessService
from src.Shared.Events.Models import EventDispatcher, BaseEvent
from src.Shared.Logging.Interfaces import ILogger


class TestCommand:
    """Test cases for RegisterUser Command class."""

    def test_init_with_valid_data(self):
        """Test Command initialization with valid data."""
        command = Command(email="test@example.com", username="testuser", password="password123")

        assert command.email == "test@example.com"
        assert command.username == "testuser"
        assert command.password == "password123"

    def test_init_with_minimum_valid_data(self):
        """Test Command initialization with minimum valid data lengths."""
        command = Command(
            email="a@b.co",
            username="abc",  # minimum 3 characters
            password="12345678",  # minimum 8 characters
        )

        assert command.email == "a@b.co"
        assert command.username == "abc"
        assert command.password == "12345678"

    def test_init_with_maximum_valid_data(self):
        """Test Command initialization with maximum valid data lengths."""
        max_username = "a" * 50  # maximum 50 characters
        max_password = "a" * 128  # maximum 128 characters

        command = Command(email="test@example.com", username=max_username, password=max_password)

        assert command.username == max_username
        assert command.password == max_password

    def test_invalid_email_format(self):
        """Test Command validation with invalid email format."""
        with pytest.raises(ValidationError) as exc_info:
            Command(email="invalid-email", username="testuser", password="password123")

        error_details = exc_info.value.errors()
        assert any(
            "value is not a valid email address" in str(error).lower() for error in error_details
        )

    def test_username_too_short(self):
        """Test Command validation with username shorter than minimum."""
        with pytest.raises(ValidationError) as exc_info:
            Command(
                email="test@example.com",
                username="ab",  # Only 2 characters, minimum is 3
                password="password123",
            )

        error_details = exc_info.value.errors()
        assert any("at least 3 characters" in str(error).lower() for error in error_details)

    def test_username_too_long(self):
        """Test Command validation with username longer than maximum."""
        long_username = "a" * 51  # 51 characters, maximum is 50

        with pytest.raises(ValidationError) as exc_info:
            Command(email="test@example.com", username=long_username, password="password123")

        error_details = exc_info.value.errors()
        assert any("at most 50 characters" in str(error).lower() for error in error_details)

    def test_password_too_short(self):
        """Test Command validation with password shorter than minimum."""
        with pytest.raises(ValidationError) as exc_info:
            Command(
                email="test@example.com",
                username="testuser",
                password="1234567",  # Only 7 characters, minimum is 8
            )

        error_details = exc_info.value.errors()
        assert any("at least 8 characters" in str(error).lower() for error in error_details)

    def test_password_too_long(self):
        """Test Command validation with password longer than maximum."""
        long_password = "a" * 129  # 129 characters, maximum is 128

        with pytest.raises(ValidationError) as exc_info:
            Command(email="test@example.com", username="testuser", password=long_password)

        error_details = exc_info.value.errors()
        assert any("at most 128 characters" in str(error).lower() for error in error_details)

    def test_empty_email(self):
        """Test Command validation with empty email."""
        with pytest.raises(ValidationError):
            Command(email="", username="testuser", password="password123")

    def test_empty_username(self):
        """Test Command validation with empty username."""
        with pytest.raises(ValidationError):
            Command(email="test@example.com", username="", password="password123")

    def test_empty_password(self):
        """Test Command validation with empty password."""
        with pytest.raises(ValidationError):
            Command(email="test@example.com", username="testuser", password="")

    def test_special_characters_in_username(self):
        """Test Command with special characters in username."""
        command = Command(email="test@example.com", username="user_123", password="password123")

        assert command.username == "user_123"

    def test_special_characters_in_password(self):
        """Test Command with special characters in password."""
        command = Command(email="test@example.com", username="testuser", password="P@ssw0rd!")

        assert command.password == "P@ssw0rd!"

    def test_unicode_characters(self):
        """Test Command with unicode characters."""
        command = Command(email="test@example.com", username="üser123", password="pássw0rd")

        assert command.username == "üser123"
        assert command.password == "pássw0rd"

    def test_field_types(self):
        """Test that fields have correct types."""
        command = Command(email="test@example.com", username="testuser", password="password123")

        assert isinstance(command.email, str)
        assert isinstance(command.username, str)
        assert isinstance(command.password, str)

    def test_pydantic_serialization(self):
        """Test that Command can be serialized properly."""
        command = Command(email="test@example.com", username="testuser", password="password123")

        data = command.model_dump()
        expected = {"email": "test@example.com", "username": "testuser", "password": "password123"}
        assert data == expected

    def test_pydantic_deserialization(self):
        """Test that Command can be deserialized from dict."""
        data = {"email": "test@example.com", "username": "testuser", "password": "password123"}

        command = Command(**data)
        assert command.email == "test@example.com"
        assert command.username == "testuser"
        assert command.password == "password123"


class TestHandler:
    """Test cases for RegisterUser Handler class."""

    @pytest.fixture
    def mock_user_repository(self):
        """Create a mock user repository."""
        return Mock(spec=IUserRepository)

    @pytest.fixture
    def mock_hashing_service(self):
        """Create a mock hashing service."""
        return Mock(spec=IHashingService)

    @pytest.fixture
    def mock_uniqueness_service(self):
        """Create a mock uniqueness service."""
        return Mock(spec=UniquenessService)

    @pytest.fixture
    def mock_event_dispatcher(self):
        """Create a mock event dispatcher."""
        return Mock(spec=EventDispatcher)

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger."""
        return Mock(spec=ILogger)

    @pytest.fixture
    def handler(
        self,
        mock_user_repository,
        mock_hashing_service,
        mock_uniqueness_service,
        mock_event_dispatcher,
        mock_logger,
    ):
        """Create a Handler instance with mocked dependencies."""
        return Handler(
            userRepository=mock_user_repository,
            hashingService=mock_hashing_service,
            uniquenessService=mock_uniqueness_service,
            eventDispatcher=mock_event_dispatcher,
            logger=mock_logger,
        )

    @pytest.fixture
    def valid_command(self):
        """Create a valid command for testing."""
        return Command(email="test@example.com", username="testuser", password="password123")

    @pytest.fixture
    def sample_user_id(self):
        """Create a sample UUID for testing."""
        return uuid4()

    def test_init(
        self,
        mock_user_repository,
        mock_hashing_service,
        mock_uniqueness_service,
        mock_event_dispatcher,
        mock_logger,
    ):
        """Test Handler initialization."""
        handler = Handler(
            userRepository=mock_user_repository,
            hashingService=mock_hashing_service,
            uniquenessService=mock_uniqueness_service,
            eventDispatcher=mock_event_dispatcher,
            logger=mock_logger,
        )

        assert handler.userRepository is mock_user_repository
        assert handler.hashingService is mock_hashing_service
        assert handler.uniquenessService is mock_uniqueness_service
        assert handler.eventDispatcher is mock_event_dispatcher
        assert handler.logger is mock_logger

    def test_handle_successful_registration(
        self,
        handler,
        valid_command,
        sample_user_id,
        mock_uniqueness_service,
        mock_hashing_service,
        mock_user_repository,
        mock_event_dispatcher,
    ):
        """Test successful user registration flow."""
        # Setup mocks
        mock_hashing_service.Hash.return_value = "hashed_password"
        mock_user = Mock(spec=User)
        mock_user.id = sample_user_id
        mock_user.ReleaseEvents.return_value = [Mock(spec=BaseEvent)]

        with patch.object(User, "Create", return_value=mock_user) as mock_create:
            result = handler.Handle(valid_command)

            # Verify uniqueness validation
            mock_uniqueness_service.ValidateIsEmailUnique.assert_called_once_with(
                "test@example.com"
            )
            mock_uniqueness_service.ValidateIsUsernameUnique.assert_called_once_with("testuser")

            # Verify password hashing
            mock_hashing_service.Hash.assert_called_once_with("password123")

            # Verify user creation
            mock_create.assert_called_once_with(
                email="test@example.com", username="testuser", passwordHash="hashed_password"
            )

            # Verify user saving
            mock_user_repository.Save.assert_called_once_with(mock_user)

            # Verify event dispatching
            mock_user.ReleaseEvents.assert_called_once()
            mock_event_dispatcher.DispatchAll.assert_called_once()

            # Verify return value
            assert result == sample_user_id

    def test_handle_email_not_unique(self, handler, valid_command, mock_uniqueness_service):
        """Test handling when email is not unique."""
        # Make email validation fail
        mock_uniqueness_service.ValidateIsEmailUnique.side_effect = ValueError(
            "Email already in use"
        )

        with pytest.raises(ValueError, match="Email already in use"):
            handler.Handle(valid_command)

        # Verify email validation was called
        mock_uniqueness_service.ValidateIsEmailUnique.assert_called_once_with("test@example.com")

        # Verify username validation was not called (short-circuited)
        mock_uniqueness_service.ValidateIsUsernameUnique.assert_not_called()

    def test_handle_username_not_unique(self, handler, valid_command, mock_uniqueness_service):
        """Test handling when username is not unique."""
        # Make username validation fail
        mock_uniqueness_service.ValidateIsUsernameUnique.side_effect = ValueError(
            "Username already in use"
        )

        with pytest.raises(ValueError, match="Username already in use"):
            handler.Handle(valid_command)

        # Verify both validations were called
        mock_uniqueness_service.ValidateIsEmailUnique.assert_called_once_with("test@example.com")
        mock_uniqueness_service.ValidateIsUsernameUnique.assert_called_once_with("testuser")

    def test_handle_with_different_command_data(
        self, handler, mock_uniqueness_service, mock_hashing_service, sample_user_id
    ):
        """Test Handle method with different command data."""
        command = Command(
            email="different@example.com", username="differentuser", password="differentpass"
        )

        mock_hashing_service.Hash.return_value = "different_hashed_password"
        mock_user = Mock(spec=User)
        mock_user.id = sample_user_id
        mock_user.ReleaseEvents.return_value = []

        with patch.object(User, "Create", return_value=mock_user) as mock_create:
            result = handler.Handle(command)

            # Verify validation with different data
            mock_uniqueness_service.ValidateIsEmailUnique.assert_called_once_with(
                "different@example.com"
            )
            mock_uniqueness_service.ValidateIsUsernameUnique.assert_called_once_with(
                "differentuser"
            )

            # Verify password hashing with different password
            mock_hashing_service.Hash.assert_called_once_with("differentpass")

            # Verify user creation with different data
            mock_create.assert_called_once_with(
                email="different@example.com",
                username="differentuser",
                passwordHash="different_hashed_password",
            )

            assert result == sample_user_id

    def test_handle_with_empty_events(
        self, handler, valid_command, sample_user_id, mock_event_dispatcher
    ):
        """Test handling when user has no events to release."""
        mock_user = Mock(spec=User)
        mock_user.id = sample_user_id
        mock_user.ReleaseEvents.return_value = []  # No events

        with patch.object(User, "Create", return_value=mock_user):
            result = handler.Handle(valid_command)

            # Verify event dispatcher is still called with empty list
            mock_event_dispatcher.DispatchAll.assert_called_once_with([])
            assert result == sample_user_id

    def test_handle_with_multiple_events(
        self, handler, valid_command, sample_user_id, mock_event_dispatcher
    ):
        """Test handling when user has multiple events to release."""
        mock_user = Mock(spec=User)
        mock_user.id = sample_user_id
        mock_events = [Mock(spec=BaseEvent), Mock(spec=BaseEvent), Mock(spec=BaseEvent)]
        mock_user.ReleaseEvents.return_value = mock_events

        with patch.object(User, "Create", return_value=mock_user):
            result = handler.Handle(valid_command)

            # Verify event dispatcher is called with multiple events
            mock_event_dispatcher.DispatchAll.assert_called_once_with(mock_events)
            assert result == sample_user_id

    def test_handle_hashing_service_error(self, handler, valid_command, mock_hashing_service):
        """Test handling when hashing service raises an error."""
        mock_hashing_service.Hash.side_effect = Exception("Hashing failed")

        with pytest.raises(Exception, match="Hashing failed"):
            handler.Handle(valid_command)

        # Verify hashing was attempted
        mock_hashing_service.Hash.assert_called_once_with("password123")

    def test_handle_user_creation_error(self, handler, valid_command, mock_hashing_service):
        """Test handling when user creation fails."""
        mock_hashing_service.Hash.return_value = "hashed_password"

        with patch.object(User, "Create", side_effect=Exception("User creation failed")):
            with pytest.raises(Exception, match="User creation failed"):
                handler.Handle(valid_command)

    def test_handle_repository_save_error(
        self, handler, valid_command, sample_user_id, mock_user_repository
    ):
        """Test handling when repository save fails."""
        mock_user = Mock(spec=User)
        mock_user.id = sample_user_id
        mock_user_repository.Save.side_effect = Exception("Database error")

        with patch.object(User, "Create", return_value=mock_user):
            with pytest.raises(Exception, match="Database error"):
                handler.Handle(valid_command)

            # Verify save was attempted
            mock_user_repository.Save.assert_called_once_with(mock_user)

    def test_handle_event_dispatch_error(
        self, handler, valid_command, sample_user_id, mock_event_dispatcher
    ):
        """Test handling when event dispatch fails."""
        mock_user = Mock(spec=User)
        mock_user.id = sample_user_id
        mock_user.ReleaseEvents.return_value = [Mock(spec=BaseEvent)]
        mock_event_dispatcher.DispatchAll.side_effect = Exception("Event dispatch failed")

        with patch.object(User, "Create", return_value=mock_user):
            with pytest.raises(Exception, match="Event dispatch failed"):
                handler.Handle(valid_command)

            # Verify event dispatch was attempted
            mock_event_dispatcher.DispatchAll.assert_called_once()

    def test_handle_execution_order(self, handler, valid_command, sample_user_id):
        """Test that Handle method executes steps in correct order."""
        # Create a mock that tracks call order
        call_order = []

        def track_email_validation(email):
            call_order.append("email_validation")

        def track_username_validation(username):
            call_order.append("username_validation")

        def track_password_hashing(password):
            call_order.append("password_hashing")
            return "hashed_password"

        def track_user_creation(*args, **kwargs):
            call_order.append("user_creation")
            mock_user = Mock(spec=User)
            mock_user.id = sample_user_id
            mock_user.ReleaseEvents.return_value = []
            return mock_user

        def track_user_save(user):
            call_order.append("user_save")

        def track_event_dispatch(events):
            call_order.append("event_dispatch")

        # Setup mocks with tracking
        handler.uniquenessService.ValidateIsEmailUnique.side_effect = track_email_validation
        handler.uniquenessService.ValidateIsUsernameUnique.side_effect = track_username_validation
        handler.hashingService.Hash.side_effect = track_password_hashing
        handler.userRepository.Save.side_effect = track_user_save
        handler.eventDispatcher.DispatchAll.side_effect = track_event_dispatch

        with patch.object(User, "Create", side_effect=track_user_creation):
            handler.Handle(valid_command)

        # Verify execution order
        expected_order = [
            "email_validation",
            "username_validation",
            "password_hashing",
            "user_creation",
            "user_save",
            "event_dispatch",
        ]
        assert call_order == expected_order

    def test_handle_password_security(self, handler, valid_command, mock_hashing_service):
        """Test that password is properly hashed and original is not stored."""
        mock_hashing_service.Hash.return_value = "securely_hashed_password"
        mock_user = Mock(spec=User)
        mock_user.id = uuid4()
        mock_user.ReleaseEvents.return_value = []

        with patch.object(User, "Create", return_value=mock_user) as mock_create:
            handler.Handle(valid_command)

            # Verify original password is passed to hashing service
            mock_hashing_service.Hash.assert_called_once_with("password123")

            # Verify only hashed password is used in user creation
            mock_create.assert_called_once_with(
                email="test@example.com",
                username="testuser",
                passwordHash="securely_hashed_password",
            )

            # Verify original password is not in the call arguments
            call_args = mock_create.call_args
            assert "password123" not in str(call_args)
            assert "securely_hashed_password" in str(call_args)

    def test_dependency_injection_integrity(self):
        """Test that Handler properly maintains dependency injection integrity."""
        # Create specific mock instances
        repo_mock = Mock(spec=IUserRepository)
        hashing_mock = Mock(spec=IHashingService)
        uniqueness_mock = Mock(spec=UniquenessService)
        dispatcher_mock = Mock(spec=EventDispatcher)
        logger_mock = Mock(spec=ILogger)

        # Create handler with these dependencies
        handler = Handler(
            userRepository=repo_mock,
            hashingService=hashing_mock,
            uniquenessService=uniqueness_mock,
            eventDispatcher=dispatcher_mock,
            logger=logger_mock,
        )

        # Verify dependencies are stored correctly
        assert handler.userRepository is repo_mock
        assert handler.hashingService is hashing_mock
        assert handler.uniquenessService is uniqueness_mock
        assert handler.eventDispatcher is dispatcher_mock
        assert handler.logger is logger_mock

    def test_command_immutability_during_handling(self, handler, valid_command):
        """Test that command data is not modified during handling."""
        original_email = valid_command.email
        original_username = valid_command.username
        original_password = valid_command.password

        mock_user = Mock(spec=User)
        mock_user.id = uuid4()
        mock_user.ReleaseEvents.return_value = []

        with patch.object(User, "Create", return_value=mock_user):
            handler.Handle(valid_command)

        # Verify command data hasn't changed
        assert valid_command.email == original_email
        assert valid_command.username == original_username
        assert valid_command.password == original_password
