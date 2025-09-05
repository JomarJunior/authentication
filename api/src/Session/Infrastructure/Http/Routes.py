from uuid import UUID
from fastapi import APIRouter, status
from src.Session.Application.CreateSession import CreateSessionCommand
from src.Session.Infrastructure.Http.Controller import SessionController
from src.Session.Application.ValidateSession import ValidateSessionCommand


class Routes:
    @classmethod
    def RegisterRoutes(cls, router: APIRouter, controller: SessionController):
        @router.post("/sessions")
        async def CreateSession(command: CreateSessionCommand):
            return controller.CreateSession(command)

        @router.post("/sessions/{sessionId}/validate", status_code=status.HTTP_204_NO_CONTENT)
        async def ValidateSession(sessionId: UUID, command: ValidateSessionCommand):
            command.sessionId = sessionId
            return controller.ValidateSession(command)

        @router.get("/sessions/health")
        async def HealthCheck():
            return {"status": "ok"}
