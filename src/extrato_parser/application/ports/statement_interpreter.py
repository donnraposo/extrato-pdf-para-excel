from abc import ABC, abstractmethod
from pathlib import Path

from ...domain.entities import ParseResult, PhysicalLine


class StatementInterpreter(ABC):
    @abstractmethod
    def interpret(self, lines: list[PhysicalLine], source: Path, page_count: int) -> ParseResult:
        raise NotImplementedError
