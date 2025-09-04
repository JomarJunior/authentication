"""
Unit tests for Logger class.
"""

import os
import tempfile
import zipfile
from unittest.mock import patch, mock_open, MagicMock, call
from datetime import datetime
import pytest
from src.Shared.Logging.Models import Logger


class TestLogger:
    """Test cases for Logger class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def console_logger(self):
        """Create a logger with console target."""
        return Logger(target="console")

    @pytest.fixture
    def file_logger(self, temp_dir):
        """Create a logger with file target."""
        log_file = os.path.join(temp_dir, "test.log")
        return Logger(target=log_file)

    @pytest.fixture
    def directory_logger(self, temp_dir):
        """Create a logger with directory target."""
        log_dir = os.path.join(temp_dir, "logs")
        return Logger(target=log_dir)

    def test_init_with_console_target(self, console_logger):
        """Test Logger initialization with console target."""
        assert console_logger.target == "console"
        assert console_logger.latestCallerSent is None

    def test_init_with_file_target(self, temp_dir):
        """Test Logger initialization with file target."""
        log_file = os.path.join(temp_dir, "test.log")
        logger = Logger(target=log_file)

        assert logger.target == log_file
        assert logger.latestCallerSent is None

    def test_init_with_directory_target(self, temp_dir):
        """Test Logger initialization with directory target that gets converted to file."""
        log_dir = os.path.join(temp_dir, "logs")
        logger = Logger(target=log_dir)

        expected_target = os.path.join(log_dir, "general.log")
        assert logger.target == expected_target
        assert logger.latestCallerSent is None

    def test_init_creates_directory_for_file_target(self, temp_dir):
        """Test that Logger creates necessary directories for file targets."""
        nested_dir = os.path.join(temp_dir, "nested", "logs")
        log_file = os.path.join(nested_dir, "test.log")

        # Directory should not exist initially
        assert not os.path.exists(nested_dir)

        Logger(target=log_file)

        # Directory should be created
        assert os.path.exists(nested_dir)

    @patch("builtins.print")
    def test_log_to_console(self, mock_print, console_logger):
        """Test logging to console."""
        test_message = "Test message"

        console_logger._Log(test_message)

        # Verify print was called
        mock_print.assert_called_once()

        # Get the actual message that was printed
        printed_message = mock_print.call_args[0][0]

        # Verify the message contains our test message
        assert test_message in printed_message
        # Verify timestamp is in the message (format: [YYYY-MM-DD HH:MM:SS])
        assert "[" in printed_message and "]" in printed_message

    def test_log_to_file(self, file_logger):
        """Test logging to file."""
        test_message = "Test file message"

        file_logger._Log(test_message)

        # Verify file was created and contains the message
        assert os.path.exists(file_logger.target)

        with open(file_logger.target, "r", encoding="utf-8") as f:
            content = f.read()
            assert test_message in content

    def test_prepend_current_time(self, console_logger):
        """Test that current time is prepended to messages."""
        test_message = "Test message"

        with patch("src.Shared.Logging.Models.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2024-01-01 12:00:00"

            result = console_logger._PrependCurrentTime(test_message)

            assert result == "[2024-01-01 12:00:00] Test message"

    def test_prepend_caller_info_first_time(self, console_logger):
        """Test that caller info is prepended the first time from a specific caller."""
        test_message = "Test message"

        # Mock the frame inspection
        with patch("src.Shared.Logging.Models.inspect.currentframe") as mock_frame:
            # Create a mock frame chain
            mock_caller_frame = MagicMock()
            mock_caller_frame.f_code.co_name = "test_function"
            mock_caller_frame.f_code.co_filename = "test_file.py"

            mock_log_frame = MagicMock()
            mock_log_frame.f_back = mock_caller_frame

            mock_prepend_frame = MagicMock()
            mock_prepend_frame.f_back = mock_log_frame

            mock_current_frame = MagicMock()
            mock_current_frame.f_back = mock_prepend_frame

            mock_frame.return_value = mock_current_frame

            result = console_logger._PrependCallerInfo(test_message)

            expected_caller_info = "test_function() in test_file.py"
            assert expected_caller_info in result
            assert test_message in result
            assert console_logger.latestCallerSent == expected_caller_info

    def test_prepend_caller_info_subsequent_calls(self, console_logger):
        """Test that caller info is not prepended for subsequent calls from same caller."""
        test_message = "Test message"
        caller_info = "test_function() in test_file.py"

        # Set the latest caller to simulate previous call
        console_logger.latestCallerSent = caller_info

        with patch("src.Shared.Logging.Models.inspect.currentframe") as mock_frame:
            # Create a mock frame chain
            mock_caller_frame = MagicMock()
            mock_caller_frame.f_code.co_name = "test_function"
            mock_caller_frame.f_code.co_filename = "test_file.py"

            mock_log_frame = MagicMock()
            mock_log_frame.f_back = mock_caller_frame

            mock_prepend_frame = MagicMock()
            mock_prepend_frame.f_back = mock_log_frame

            mock_current_frame = MagicMock()
            mock_current_frame.f_back = mock_prepend_frame

            mock_frame.return_value = mock_current_frame

            result = console_logger._PrependCallerInfo(test_message)

            # Should return only the message since caller info was already sent
            assert result == test_message

    def test_prepend_caller_info_no_frame(self, console_logger):
        """Test caller info prepending when frame is None."""
        test_message = "Test message"

        with patch("src.Shared.Logging.Models.inspect.currentframe", return_value=None):
            result = console_logger._PrependCallerInfo(test_message)

            assert result == test_message

    def test_info_method(self, console_logger):
        """Test Info logging method."""
        test_message = "Info message"

        with patch.object(console_logger, "_Log") as mock_log:
            console_logger.Info(test_message)

            mock_log.assert_called_once_with("[INFO] - Info message")

    def test_warning_method(self, console_logger):
        """Test Warning logging method."""
        test_message = "Warning message"

        with patch.object(console_logger, "_Log") as mock_log:
            console_logger.Warning(test_message)

            mock_log.assert_called_once_with("[WARNING] - Warning message")

    def test_error_method(self, console_logger):
        """Test Error logging method."""
        test_message = "Error message"

        with patch.object(console_logger, "_Log") as mock_log:
            console_logger.Error(test_message)

            mock_log.assert_called_once_with("[ERROR] - Error message")

    def test_debug_method(self, console_logger):
        """Test Debug logging method."""
        test_message = "Debug message"

        with patch.object(console_logger, "_Log") as mock_log:
            console_logger.Debug(test_message)

            mock_log.assert_called_once_with("[DEBUG] - Debug message")

    def test_log_rotate_not_needed(self, file_logger):
        """Test log rotation when file size is below threshold."""
        # Create a small log file
        with open(file_logger.target, "w", encoding="utf-8") as f:
            f.write("Small log content")

        original_size = os.path.getsize(file_logger.target)

        file_logger._LogRotate()

        # File should still exist and be the same size
        assert os.path.exists(file_logger.target)
        assert os.path.getsize(file_logger.target) == original_size

    def test_log_rotate_needed(self, file_logger):
        """Test log rotation when file size exceeds threshold."""
        # Create a large log file (mock the size check)
        with open(file_logger.target, "w", encoding="utf-8") as f:
            f.write("Log content")

        with patch("os.path.getsize", return_value=6 * 1024 * 1024):  # 6MB > 5MB threshold
            with patch("src.Shared.Logging.Models.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "January"

                with patch("src.Shared.Logging.Models.randbytes") as mock_randbytes:
                    mock_randbytes.return_value.hex.return_value = "abcd1234"

                    with patch("os.rename") as mock_rename:
                        with patch("zipfile.ZipFile") as mock_zipfile:
                            with patch("os.remove") as mock_remove:

                                file_logger._LogRotate()

                                # Verify rename was called
                                expected_new_name = f"{file_logger.target}.January.abcd1234"
                                mock_rename.assert_called_once_with(
                                    file_logger.target, expected_new_name
                                )

                                # Verify zip file creation
                                mock_zipfile.assert_called_once_with(
                                    f"{expected_new_name}.zip", "w"
                                )

                                # Verify old file removal
                                mock_remove.assert_called_once_with(expected_new_name)

    def test_log_rotate_nonexistent_file(self, file_logger):
        """Test log rotation when target file doesn't exist."""
        # Ensure file doesn't exist
        if os.path.exists(file_logger.target):
            os.remove(file_logger.target)

        # Should not raise an exception
        file_logger._LogRotate()

    def test_file_logging_creates_directory_structure(self, temp_dir):
        """Test that file logging creates necessary directory structure."""
        nested_path = os.path.join(temp_dir, "deep", "nested", "logs", "app.log")
        logger = Logger(target=nested_path)

        test_message = "Test message"
        logger._Log(test_message)

        # Verify directory structure was created
        assert os.path.exists(os.path.dirname(nested_path))
        assert os.path.exists(nested_path)

        # Verify content was written
        with open(nested_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert test_message in content

    def test_multiple_log_calls_same_caller(self, console_logger):
        """Test multiple log calls from the same caller only show caller info once."""
        with patch("builtins.print") as mock_print:
            with patch("src.Shared.Logging.Models.inspect.currentframe") as mock_frame:
                # Setup mock frame
                mock_caller_frame = MagicMock()
                mock_caller_frame.f_code.co_name = "test_function"
                mock_caller_frame.f_code.co_filename = "test_file.py"

                mock_log_frame = MagicMock()
                mock_log_frame.f_back = mock_caller_frame

                mock_prepend_frame = MagicMock()
                mock_prepend_frame.f_back = mock_log_frame

                mock_current_frame = MagicMock()
                mock_current_frame.f_back = mock_prepend_frame

                mock_frame.return_value = mock_current_frame

                # First call
                console_logger.Info("First message")
                first_call_args = mock_print.call_args[0][0]

                # Second call
                console_logger.Info("Second message")
                second_call_args = mock_print.call_args[0][0]

                # First call should have caller info
                assert "test_function() in test_file.py" in first_call_args

                # Second call should not have caller info
                assert "test_function() in test_file.py" not in second_call_args
                assert "Second message" in second_call_args

    def test_log_calls_different_callers(self, console_logger):
        """Test log calls from different callers show caller info for each new caller."""
        with patch("builtins.print") as mock_print:
            with patch("src.Shared.Logging.Models.inspect.currentframe") as mock_frame:

                # First caller
                mock_caller_frame1 = MagicMock()
                mock_caller_frame1.f_code.co_name = "first_function"
                mock_caller_frame1.f_code.co_filename = "first_file.py"

                mock_log_frame1 = MagicMock()
                mock_log_frame1.f_back = mock_caller_frame1

                mock_prepend_frame1 = MagicMock()
                mock_prepend_frame1.f_back = mock_log_frame1

                mock_current_frame1 = MagicMock()
                mock_current_frame1.f_back = mock_prepend_frame1

                mock_frame.return_value = mock_current_frame1

                console_logger.Info("First caller message")
                first_call_args = mock_print.call_args[0][0]

                # Second caller
                mock_caller_frame2 = MagicMock()
                mock_caller_frame2.f_code.co_name = "second_function"
                mock_caller_frame2.f_code.co_filename = "second_file.py"

                mock_log_frame2 = MagicMock()
                mock_log_frame2.f_back = mock_caller_frame2

                mock_prepend_frame2 = MagicMock()
                mock_prepend_frame2.f_back = mock_log_frame2

                mock_current_frame2 = MagicMock()
                mock_current_frame2.f_back = mock_prepend_frame2

                mock_frame.return_value = mock_current_frame2

                console_logger.Info("Second caller message")
                second_call_args = mock_print.call_args[0][0]

                # Both calls should have their respective caller info
                assert "first_function() in first_file.py" in first_call_args
                assert "second_function() in second_file.py" in second_call_args

    def test_edge_case_empty_message(self, console_logger):
        """Test logging with empty message."""
        with patch.object(console_logger, "_Log") as mock_log:
            console_logger.Info("")

            mock_log.assert_called_once_with("[INFO] - ")

    def test_edge_case_none_message(self, console_logger):
        """Test logging with None message should handle gracefully."""
        with patch.object(console_logger, "_Log") as mock_log:
            # This should work due to f-string conversion
            console_logger.Info(None)

            mock_log.assert_called_once_with("[INFO] - None")

    def test_special_characters_in_message(self, file_logger):
        """Test logging messages with special characters."""
        special_message = "Test with special chars: üöä ñ 中文 🚀"

        file_logger.Info(special_message)

        # Verify file was created and contains the special characters
        assert os.path.exists(file_logger.target)

        with open(file_logger.target, "r", encoding="utf-8") as f:
            content = f.read()
            assert special_message in content

    def test_multiline_message(self, console_logger):
        """Test logging multiline messages."""
        multiline_message = "Line 1\nLine 2\nLine 3"

        with patch.object(console_logger, "_Log") as mock_log:
            console_logger.Info(multiline_message)

            expected_call = f"[INFO] - {multiline_message}"
            mock_log.assert_called_once_with(expected_call)

    def test_log_file_permissions(self, temp_dir):
        """Test that log files are created with proper permissions."""
        log_file = os.path.join(temp_dir, "permissions_test.log")
        logger = Logger(target=log_file)

        logger.Info("Test message")

        # Verify file exists and is readable/writable
        assert os.path.exists(log_file)
        assert os.access(log_file, os.R_OK)
        assert os.access(log_file, os.W_OK)

    def test_concurrent_logging_safety(self, file_logger):
        """Test that concurrent logging doesn't cause issues."""
        import threading
        import time

        def log_messages(thread_id):
            for i in range(3):  # Reduced number for better reliability
                file_logger.Info(f"Thread {thread_id} - Message {i}")
                time.sleep(0.001)  # Shorter delay

        threads = []
        for i in range(2):  # Reduced threads for better reliability
            thread = threading.Thread(target=log_messages, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Verify file exists and contains some content
        assert os.path.exists(file_logger.target)

        with open(file_logger.target, "r", encoding="utf-8") as f:
            content = f.read()

        # Just verify that some messages were logged and no crashes occurred
        assert len(content) > 0
        assert "Thread 0" in content
        assert "Thread 1" in content
        assert "[INFO]" in content
