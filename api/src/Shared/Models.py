from datetime import datetime, timezone
from pydantic import BaseModel, Field
from src.Shared.Enums import AuthenticationMethodEnum


class HistoryClass(BaseModel):
    """
    HistoryClass is a model that tracks creation and update timestamps.
    Attributes:
        createdAt (datetime):
            The timestamp indicating when the instance was created.
            Defaults to the current UTC time.
        updatedAt (datetime):
            The timestamp indicating when the instance was last updated.
            Defaults to the current UTC time.
    Methods:
        UpdateTimestamp(func):
            A static method decorator that updates the `updatedAt` timestamp
            whenever the decorated method is called.
    """

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


class AuthenticationMethod(BaseModel):
    value: AuthenticationMethodEnum = Field(...)
    _levelMap = {
        AuthenticationMethodEnum.PASSWORD: 1,
        AuthenticationMethodEnum.MFA: 2,
        AuthenticationMethodEnum.GOOGLE: 1,
        AuthenticationMethodEnum.FACEBOOK: 1,
        AuthenticationMethodEnum.GITHUB: 1,
        AuthenticationMethodEnum.TWITTER: 1,
    }

    def __str__(self):
        return self.value

    def __eq__(self, other):
        try:
            return self._levelMap[self.value] == self._levelMap[other.value]
        except (ValueError, KeyError, AttributeError):
            return False
