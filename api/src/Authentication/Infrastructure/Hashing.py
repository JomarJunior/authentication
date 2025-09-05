import bcrypt

from src.Authentication.Domain.Interfaces import IHashingService


class BcryptHashingService(IHashingService):
    def __init__(self, rounds: int = 12, prefix: bytes = b"2b") -> None:
        self.rounds = rounds
        self.prefix = prefix

    def Hash(self, plainText: str) -> str:
        salt = bcrypt.gensalt(rounds=self.rounds, prefix=self.prefix)
        return bcrypt.hashpw(plainText.encode("utf-8"), salt).decode("utf-8")

    def Verify(self, plainText: str, hashed: str) -> bool:
        return bcrypt.checkpw(plainText.encode("utf-8"), hashed.encode("utf-8"))
