from src.Authentication.Domain.Interfaces import IUserRepository


class UniquenessService:
    def __init__(self, userRepository: IUserRepository):
        self.userRepository = userRepository

    def ValidateIsEmailUnique(self, email: str) -> None:
        if self.userRepository.FindByEmail(email) is not None:
            raise ValueError("Email already in use")

    def ValidateIsUsernameUnique(self, username: str) -> None:
        if self.userRepository.FindByUsername(username) is not None:
            raise ValueError("Username already in use")
