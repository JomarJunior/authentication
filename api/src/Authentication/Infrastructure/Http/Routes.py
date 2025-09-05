from typing import Optional
from fastapi import APIRouter, status
from src.Authentication.Infrastructure.Http.Controller import AuthenticationController
from src.Authentication.Application.ListAllUsers import ListAllUsersCommand
from src.Authentication.Application.RegisterUser import RegisterUserCommand


class Routes:
    @classmethod
    def RegisterRoutes(cls, router: APIRouter, controller: AuthenticationController):
        @router.get("/users")
        async def ListAllUsers(command: Optional[ListAllUsersCommand] = None):
            return controller.ListAllUsers(command)

        @router.post("/users")
        async def RegisterUser(command: RegisterUserCommand):
            return controller.RegisterUser(command)
