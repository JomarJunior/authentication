from pydantic import BaseModel, Field
from src.Authentication.Domain.Interfaces import IUserRepository, IHashingService
from src.Shared.Events.Models import EventDispatcher
from src.Shared.Logging.Interfaces import ILogger
from src.Authentication.Domain.Models import User, AuthenticationCredentials


class AuthenticateCommand(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)

    def __str__(self):
        # Avoid logging sensitive information like passwords
        return f"AuthenticateCommand(username={self.username}, password=****)"

    def __repr__(self):
        # Avoid logging sensitive information like passwords
        return self.__str__()


class AuthenticateHandler:
    def __init__(
        self,
        userRepository: IUserRepository,
        hashingService: IHashingService,
        eventDispatcher: EventDispatcher,
        logger: ILogger,
    ):
        self.userRepository = userRepository
        self.hashingService = hashingService
        self.eventDispatcher = eventDispatcher
        self.logger = logger

    def Handle(self, command: AuthenticateCommand) -> User:
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

        # Dispatch events if any (e.g., login events)
        self.eventDispatcher.DispatchAll(user.ReleaseEvents())

        self.logger.Info(f"User {user.id} authenticated successfully")
        return user
