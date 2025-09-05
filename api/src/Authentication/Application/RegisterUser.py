from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from src.Authentication.Domain.Interfaces import IHashingService, IUserRepository
from src.Authentication.Domain.Models import User
from src.Authentication.Domain.Sevices import UniquenessService
from src.Shared.Events.Models import EventDispatcher
from src.Shared.Logging.Interfaces import ILogger


class RegisterUserCommand(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class RegisterUserHandler:
    def __init__(
        self,
        userRepository: IUserRepository,
        hashingService: IHashingService,
        uniquenessService: UniquenessService,
        eventDispatcher: EventDispatcher,
        logger: ILogger,
    ):
        self.userRepository = userRepository
        self.hashingService = hashingService
        self.uniquenessService = uniquenessService
        self.eventDispatcher = eventDispatcher
        self.logger = logger

    def Handle(self, command: RegisterUserCommand) -> UUID:
        # Validate
        self.uniquenessService.ValidateIsEmailUnique(command.email)
        self.uniquenessService.ValidateIsUsernameUnique(command.username)

        # Hash the password
        passwordHash = self.hashingService.Hash(command.password)

        # Create the user
        newUser = User.Create(
            email=command.email,
            username=command.username,
            passwordHash=passwordHash,
        )

        # Save the user
        self.userRepository.Save(newUser)

        # Dispatch events
        self.eventDispatcher.DispatchAll(newUser.ReleaseEvents())

        # Return the new user's ID
        return newUser.id
