from pathlib import Path

from ...domain.entities import ParseResult, PhysicalLine
from ...normalization import plain_text
from ..statement_layout import StatementLayout


class InterStatementLayout(StatementLayout):
    def matches(self, lines: list[PhysicalLine]) -> bool:
        return any("VALOR" in plain_text(line.text) and "SALDO POR TRANSACAO" in plain_text(line.text) for line in lines)

    def parse(self, lines: list[PhysicalLine], source: Path, page_count: int) -> ParseResult:
        from ...parser import _parse_inter_lines

        return _parse_inter_lines(lines, source, page_count)
