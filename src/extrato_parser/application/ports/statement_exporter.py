from abc import ABC, abstractmethod
from pathlib import Path

from ...domain.entities import ParseResult


class StatementExporter(ABC):
    @abstractmethod
    def export(self, result: ParseResult, output: Path) -> None:
        raise NotImplementedError
