from typing import Optional
from fastapi import HTTPException
from src.Authentication.Application.ListAllUsers import (
    ListAllUsersHandler,
    ListAllUsersCommand,
)

from src.Authentication.Application.RegisterUser import (
    RegisterUserHandler,
    RegisterUserCommand,
)

from src.Authentication.Application.Authenticate import (
    AuthenticateHandler,
    AuthenticateCommand,
)

from src.Shared.Logging.Interfaces import ILogger


class AuthenticationController:
    def __init__(
        self,
        listAllUsersHandler: ListAllUsersHandler,
        registerUserHandler: RegisterUserHandler,
        authenticateHandler: AuthenticateHandler,
        logger: ILogger,
    ):
        self.listAllUsersHandler = listAllUsersHandler
        self.registerUserHandler = registerUserHandler
        self.authenticateHandler = authenticateHandler
        self.logger = logger

    def ListAllUsers(self, command: Optional[ListAllUsersCommand] = None):
        try:
            self.logger.Info(f"Listing all users with command: {command}")
            return self.listAllUsersHandler.Handle(command)
        except Exception as e:
            self.logger.Error(f"Error listing users: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    def RegisterUser(self, command: RegisterUserCommand):
        try:
            self.logger.Info(f"Registering user with command: {command}")
            return self.registerUserHandler.Handle(command)
        except Exception as e:
            self.logger.Error(f"Error registering user: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    def Authenticate(self, command: AuthenticateCommand):
        try:
            self.logger.Info(f"Authenticating user with command: {command}")
            return self.authenticateHandler.Handle(command)
        except ValueError as ve:
            self.logger.Warning(f"Authentication failed: {ve}")
            raise HTTPException(status_code=401, detail=str(ve)) from ve
        except Exception as e:
            self.logger.Error(f"Error during authentication: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e
