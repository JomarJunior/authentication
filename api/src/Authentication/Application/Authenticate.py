from uuid import UUID
from pydantic import BaseModel, Field
from src.Authentication.Domain.Interfaces import (
    IUserRepository,
    IHashingService,
    IAuthCodeRepository,
    ISessionService,
)
from src.Shared.Events.Models import EventDispatcher
from src.Shared.Logging.Interfaces import ILogger
from src.Authentication.Domain.Models import AuthenticationCredentials
from src.Authentication.Domain.Sevices import AuthenticationCodeService


class AuthenticateCommand(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    clientId: str = Field(min_length=36, max_length=36)
    codeChallenge: str = Field(min_length=43, max_length=128)
    scopes: list[str] = Field(default_factory=list)

    def __str__(self):
        # Avoid logging sensitive information like passwords
        return f"""AuthenticateCommand(
        username={self.username}, password=****, 
        clientId={self.clientId}, 
        codeChallenge=****, 
        scopes={self.scopes})
        """

    def __repr__(self):
        # Avoid logging sensitive information like passwords
        return self.__str__()


class AuthenticateHandler:
    def __init__(
        self,
        userRepository: IUserRepository,
        authCodeRepository: IAuthCodeRepository,
        hashingService: IHashingService,
        authenticationCodeService: AuthenticationCodeService,
        sessionService: ISessionService,
        eventDispatcher: EventDispatcher,
        logger: ILogger,
    ):
        self.userRepository = userRepository
        self.authCodeRepository = authCodeRepository
        self.hashingService = hashingService
        self.authenticationCodeService = authenticationCodeService
        self.sessionService = sessionService
        self.eventDispatcher = eventDispatcher
        self.logger = logger

    def Handle(self, command: AuthenticateCommand) -> tuple[str, str]:
        # Find the user by username
        user = self.userRepository.FindByUsername(command.username)
        if not user:
            self.logger.Warning(f"Authentication failed for username: {command.username}")
            raise ValueError("Invalid username or password")

        # Verify the password
        credentials: AuthenticationCredentials = user.authenticationCredentials
        if not self.hashingService.Verify(command.password, credentials.passwordHash):
            self.logger.Warning(f"Authentication failed for username: {command.username}")
            raise ValueError("Invalid username or password")

        # Generate an authentication code
        authenticationCode = self.authenticationCodeService.Generate(
            userId=user.id,
            clientId=UUID(command.clientId),
            scopes=command.scopes,
            codeChallenge=command.codeChallenge,
        )

        # Create a new session for the user
        sessionId: UUID = self.sessionService.CreatePasswordSession(
            userId=user.id,
            clientId=UUID(command.clientId),
            scopes=command.scopes,
            codeChallenge=command.codeChallenge,
            authenticationCodeId=authenticationCode.id,
        )

        # Store the authentication code
        self.authCodeRepository.Save(authenticationCode)

        # Dispatch events if any (e.g., login events)
        self.eventDispatcher.DispatchAll(authenticationCode.ReleaseEvents())

        self.logger.Info(f"User {user.id} authenticated successfully")
        return authenticationCode.code, str(sessionId)
