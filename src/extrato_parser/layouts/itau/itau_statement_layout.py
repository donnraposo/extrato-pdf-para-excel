from pathlib import Path

from ...domain.entities import ParseResult, PhysicalLine
from ...normalization import plain_text
from ..statement_layout import StatementLayout


class ItauStatementLayout(StatementLayout):
    def matches(self, lines: list[PhysicalLine]) -> bool:
        sample = plain_text(" ".join(line.text for line in lines[:60]))
        return "ITAU" in sample or ("ENTRADAS" in sample and "SAIDAS" in sample and "SALDO" in sample)

    def parse(self, lines: list[PhysicalLine], source: Path, page_count: int) -> ParseResult:
        from ...parser import _parse_generic_lines

        return _parse_generic_lines(lines, source, page_count)
