from pathlib import Path

from ..application.ports import StatementInterpreter
from ..domain.entities import ParseResult, PhysicalLine
from .layout_detector import LayoutDetector
from .layout_registry import LayoutRegistry


class LayoutStatementInterpreter(StatementInterpreter):
    def __init__(self, detector: LayoutDetector | None = None) -> None:
        self._detector = detector or LayoutDetector(LayoutRegistry().registered())

    def interpret(self, lines: list[PhysicalLine], source: Path, page_count: int) -> ParseResult:
        layout = self._detector.detect(lines)
        return layout.parse(lines, source, page_count)
