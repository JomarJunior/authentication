import os
import inspect
from datetime import datetime
from random import randbytes
import zipfile
from src.Shared.Logging.Interfaces import ILogger


class Logger(ILogger):
    """
    This class provides logging functionality for the application.
    """

    def __init__(self, target: str = "console"):
        """
        Initialize the logger with a target.
        :param target: The target for logging, e.g., 'console', 'file'.
        """
        self.target = target
        self.latestCallerSent = None
        if self.target != "console":
            os.makedirs(os.path.dirname(self.target), exist_ok=True)
            # Concat general.log to the target file if it is a file path
            if not self.target.endswith(".log"):
                self.target = os.path.join(self.target, "general.log")

    def _Log(self, message: str):
        """
        Internal method to log a message to the specified target.
        :param message: The message to log.
        """
        message = self._PrependCurrentTime(message)
        message = self._PrependCallerInfo(message)
        if self.target == "console":
            print(message)
        else:
            self._LogRotate()
            if not os.path.exists(self.target):
                os.makedirs(os.path.dirname(self.target), exist_ok=True)
            with open(self.target, "a", encoding="utf-8") as file:
                file.write(message + "\n")

    def _LogRotate(self):
        """
        Rotate the log file if it exceeds a certain size.
        """
        maxLogSize = 1024 * 1024 * 5  # 5 MB
        if self.target != "console" and os.path.exists(self.target):
            if os.path.getsize(self.target) > maxLogSize:
                # Rotate the log file by renaming it and creating a new one
                monthName: str = datetime.now().strftime("%B")
                randomBytes = randbytes(8).hex()
                newName: str = f"{self.target}.{monthName}.{randomBytes}"
                os.rename(self.target, newName)
                with open(self.target, "w", encoding="utf-8") as file:
                    file.write("")
                # Compress the old log
                with zipfile.ZipFile(f"{newName}.zip", "w") as zipf:
                    zipf.write(newName, arcname=os.path.basename(newName))
                os.remove(newName)

    def _PrependCurrentTime(self, message: str) -> str:
        """
        Prepend the current time to the log message.
        :param message: The original log message.
        :return: The modified log message with the current time.
        """
        currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{currentTime}] {message}"

    def _PrependCallerInfo(self, message: str) -> str:
        """
        Prepend caller information to the log message.
        Here we usually arrive three levels up the stack to get the caller
        function name and file information.
        This helps in identifying where the log message originated from.
        :param message: The original log message.
        :return: The modified log message with caller information.
        """
        # Get the current frame and the caller frame (
        # skip the _PrependCallerInfo method, the _Log method and the specific level method
        # )
        currentFrame = inspect.currentframe()
        if currentFrame is not None:
            # Skip the current frame
            callerFrame = currentFrame.f_back
            if callerFrame is not None:
                # Skip the _log method
                callerFrame = callerFrame.f_back
            if callerFrame is not None:
                # Get the caller function name and file information
                callerFrame = callerFrame.f_back

            # If we have a valid caller frame,
            # prepend the caller information if it is the first time
            # we are logging from this caller in the sequence of logs
            if callerFrame is not None:
                callerInfo = f"{callerFrame.f_code.co_name}() in {callerFrame.f_code.co_filename}"
                # Check if the caller info is already sent
                if self.latestCallerSent != callerInfo:
                    # Update the latest caller info
                    self.latestCallerSent = callerInfo
                    # To avoid excessive logging,
                    # we only prepend caller info once per subsequent log
                    return f"{callerInfo}\n{message}"
        return message

    def Info(self, message: str):
        """
        Log an informational message.
        :param message: The message to log.
        """
        self._Log(f"[INFO] - {message}")

    def Warning(self, message: str):
        """
        Log a warning message.
        :param message: The message to log.
        """
        self._Log(f"[WARNING] - {message}")

    def Error(self, message: str):
        """
        Log an error message.
        :param message: The message to log.
        """
        self._Log(f"[ERROR] - {message}")

    def Debug(self, message: str):
        """
        Log a debug message.
        :param message: The message to log.
        """
        self._Log(f"[DEBUG] - {message}")
