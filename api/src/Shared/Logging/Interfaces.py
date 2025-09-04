from abc import ABC, abstractmethod


class ILogger(ABC):
    @abstractmethod
    def Info(self, message: str):
        pass

    @abstractmethod
    def Warning(self, message: str):
        pass

    @abstractmethod
    def Error(self, message: str):
        pass

    @abstractmethod
    def Debug(self, message: str):
        pass
