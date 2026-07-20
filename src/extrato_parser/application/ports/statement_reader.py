from abc import ABC, abstractmethod
from pathlib import Path

from ...domain.entities import PhysicalLine


class StatementReader(ABC):
    @abstractmethod
    def read(self, path: Path) -> tuple[list[PhysicalLine], int]:
        raise NotImplementedError
