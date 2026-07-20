from pathlib import Path

from ...domain.entities import ParseResult, PhysicalLine
from ..statement_layout import StatementLayout


class GenericStatementLayout(StatementLayout):
    def matches(self, lines: list[PhysicalLine]) -> bool:
        return True

    def parse(self, lines: list[PhysicalLine], source: Path, page_count: int) -> ParseResult:
        from ...parser import _parse_generic_lines

        return _parse_generic_lines(lines, source, page_count)
