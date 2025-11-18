from abc import ABC, abstractmethod
from .models import Result


class IResultRepo(ABC):
    """
    Interface for simulation result repository.
    Write only.
    """
    @abstractmethod
    def save(self, obj: Result) -> None:
        """
        Save a result to repository.
        """
        pass
