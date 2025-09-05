from fastapi import HTTPException
from src.Session.Application.CreateSession import CreateSessionCommand, CreateSessionHandler
from src.Session.Application.ValidateSession import ValidateSessionCommand, ValidateSessionHandler
from src.Shared.Logging.Interfaces import ILogger


class SessionController:
    def __init__(
        self,
        createSessionHandler: CreateSessionHandler,
        validateSessionHandler: ValidateSessionHandler,
        logger: ILogger,
    ):
        self.createSessionHandler = createSessionHandler
        self.validateSessionHandler = validateSessionHandler
        self.logger = logger

    def CreateSession(self, command: CreateSessionCommand):
        try:
            self.logger.Info(f"Creating session with command: {command}")
            return self.createSessionHandler.Handle(command)
        except Exception as e:
            self.logger.Error(f"Error creating session: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    def ValidateSession(self, command: ValidateSessionCommand):
        try:
            self.logger.Info(f"Validating session with command: {command}")
            return self.validateSessionHandler.Handle(command)
        except ValueError as ve:
            self.logger.Warning(f"Session validation failed: {ve}")
            raise HTTPException(status_code=401, detail=str(ve)) from ve
        except Exception as e:
            self.logger.Error(f"Error validating session: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e
