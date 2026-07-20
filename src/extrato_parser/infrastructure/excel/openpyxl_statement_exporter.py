from pathlib import Path

from ...application.ports import StatementExporter
from ...domain.entities import ParseResult


class OpenpyxlStatementExporter(StatementExporter):
    def export(self, result: ParseResult, output: Path) -> None:
        from ...exporter import export_to_excel

        export_to_excel(result, output)
