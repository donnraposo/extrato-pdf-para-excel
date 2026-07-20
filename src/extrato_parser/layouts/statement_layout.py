from abc import ABC, abstractmethod
from pathlib import Path

from ..domain.entities import ParseResult, PhysicalLine


class StatementLayout(ABC):
    @abstractmethod
    def matches(self, lines: list[PhysicalLine]) -> bool:
        raise NotImplementedError

    @abstractmethod
    def parse(self, lines: list[PhysicalLine], source: Path, page_count: int) -> ParseResult:
        raise NotImplementedError
