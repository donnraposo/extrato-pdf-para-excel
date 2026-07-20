from pathlib import Path

from ...domain.entities import ParseResult, PhysicalLine
from ...normalization import plain_text
from ..statement_layout import StatementLayout


class CaixaStatementLayout(StatementLayout):
    def matches(self, lines: list[PhysicalLine]) -> bool:
        texts = [plain_text(line.text) for line in lines]
        has_columns = any("DOCUMENTO" in text and "HISTORICO" in text and "VALOR" in text and "SALDO" in text for text in texts)
        has_effective_date = any(text.strip() == "DATA EFETIVA" for text in texts)
        has_signature = any("SAC CAIXA" in text or "SALDO DIA" in text for text in texts)
        return has_columns and has_effective_date and has_signature

    def parse(self, lines: list[PhysicalLine], source: Path, page_count: int) -> ParseResult:
        from ...parser import _parse_caixa_lines

        return _parse_caixa_lines(lines, source, page_count)
