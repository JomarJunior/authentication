from typing import Optional
from src.Authentication.Application.ListAllUsers import (
    ListAllUsersHandler,
    ListAllUsersCommand,
)

from src.Authentication.Application.RegisterUser import (
    RegisterUserHandler,
    RegisterUserCommand,
)

from src.Shared.Logging.Interfaces import ILogger
from fastapi import HTTPException


class AuthenticationController:
    def __init__(
        self,
        listAllUsersHandler: ListAllUsersHandler,
        registerUserHandler: RegisterUserHandler,
        logger: ILogger,
    ):
        self.listAllUsersHandler = listAllUsersHandler
        self.registerUserHandler = registerUserHandler
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
