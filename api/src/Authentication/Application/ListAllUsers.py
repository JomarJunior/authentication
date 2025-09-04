from typing import List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from src.Authentication.Domain.Interfaces import IUserRepository
from src.Authentication.Domain.Models import User
from src.Shared.Logging.Interfaces import ILogger


class Command(BaseModel):
    sortBy: str = Field(default="id")
    sortOrder: str = Field(default="asc")
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

    @field_validator("sortBy")
    @classmethod
    def ValidateSortBy(cls, value: str) -> str:
        allowedSortFields = {"id", "email", "username", "createdAt", "updatedAt"}
        if value not in allowedSortFields:
            raise ValueError(f"sortBy must be one of {allowedSortFields}")
        return value

    @field_validator("sortOrder")
    @classmethod
    def ValidateSortOrder(cls, value: str) -> str:
        allowedSortOrders = {"asc", "desc"}
        if value not in allowedSortOrders:
            raise ValueError(f"sortOrder must be one of {allowedSortOrders}")
        return value


class Handler:
    def __init__(self, userRepository: IUserRepository, logger: ILogger):
        self.userRepository = userRepository
        self.logger = logger

    def Handle(self, command: Command) -> List[Dict[str, Any]]:
        self.logger.Info(
            f"""Listing users sorted by {command.sortBy} in 
            {command.sortOrder} order, limit {command.limit}, offset {command.offset}"""
        )
        users = self.userRepository.ListAll(
            sortBy=command.sortBy,
            sortOrder=command.sortOrder,
            limit=command.limit,
            offset=command.offset,
        )
        self.logger.Info(f"Listed {len(users)} users")
        return User.ToDicts(users)
