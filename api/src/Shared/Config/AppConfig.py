"""
App configuration settings.
"""

import os
import re
from enum import Enum
from pydantic import Field, BaseModel, field_validator


class OSType(str, Enum):
    """
    Enum for operating system types.
    """

    WINDOWS = "nt"
    LINUX = "posix"
    MACOS = "darwin"
    OTHER = "other"


class AppConfig(BaseModel):
    operatingSystem: OSType = (
        OSType(os.name) if os.name in {item.value for item in OSType} else OSType.OTHER
    )
    appName: str = Field(..., description="The name of the application")
    version: str = Field(..., description="The version of the application")
    debug: bool = Field(False, description="Enable debug mode")
    databaseUrl: str = Field(..., description="Database connection URL")
    port: int = Field(8000, description="Port number for the application server")
    host: str = Field("localhost", description="Host name for the application server")
    logTarget: str = Field(..., description="Target for logging (e.g., file, console)")
    authCodeExpiryMinutes: int = Field(5, description="Authentication code expiry time in minutes")

    @classmethod
    def FromEnv(cls):
        databaseUrl: str | None = os.getenv("DATABASE_URL")
        if not databaseUrl:
            raise ValueError("DATABASE_URL environment variable is required")

        return cls(
            appName=os.getenv("APP_NAME", "Authentication"),
            version=os.getenv("VERSION", "1.0.0"),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            databaseUrl=databaseUrl,
            port=int(os.getenv("PORT", "8000")),
            host=os.getenv("HOST", "localhost"),
            logTarget=os.getenv("LOG_TARGET", "console"),
            authCodeExpiryMinutes=int(os.getenv("AUTH_CODE_EXPIRY_MINUTES", "10")),
        )

    @field_validator("port")
    @classmethod
    def ValidatePort(cls, value: int) -> int:
        if not 0 < value < 65536:
            raise ValueError("Port must be between 1 and 65535")
        return value

    @field_validator("debug")
    @classmethod
    def ValidateDebug(cls, value: bool) -> bool:
        if not isinstance(value, bool):
            raise ValueError("Debug must be a boolean value")
        return value

    @field_validator("host")
    @classmethod
    def ValidateHost(cls, value: str) -> str:
        if not value:
            raise ValueError("Host cannot be empty")
        return value

    @field_validator("appName")
    @classmethod
    def ValidateAppName(cls, value: str) -> str:
        if not value:
            raise ValueError("Application name cannot be empty")
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValueError(
                "Application name must contain only alphanumeric characters and underscores"
            )
        return value

    @field_validator("version")
    @classmethod
    def ValidateVersion(cls, value: str) -> str:
        if not value:
            raise ValueError("Version cannot be empty")
        versionRegex = r"^\d+\.\d+\.\d+$"
        if not re.match(versionRegex, value):
            raise ValueError("Version must be in the format X.Y.Z")
        return value

    def ToDict(self) -> dict:
        return {
            "appName": self.appName,
            "version": self.version,
            "debug": self.debug,
            "databaseUrl": self.databaseUrl,
            "port": self.port,
            "host": self.host,
            "logTarget": self.logTarget,
        }
