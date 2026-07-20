from pathlib import Path

from ...domain.entities import ParseResult
from ..ports import StatementExporter, StatementInterpreter, StatementReader


class ConvertStatement:
    def __init__(self, reader: StatementReader, interpreter: StatementInterpreter, exporter: StatementExporter) -> None:
        self._reader = reader
        self._interpreter = interpreter
        self._exporter = exporter

    def execute(self, pdf_path: Path, output_path: Path) -> ParseResult:
        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError("Selecione um arquivo PDF.")
        if not pdf_path.is_file():
            raise FileNotFoundError("O arquivo PDF selecionado não existe.")
        if output_path.suffix.lower() != ".xlsx":
            output_path = output_path.with_suffix(".xlsx")
        lines, page_count = self._reader.read(pdf_path)
        result = self._interpreter.interpret(lines, pdf_path, page_count)
        if not result.entries and result.rejected_lines:
            reasons = "; ".join(item[2] for item in result.rejected_lines[:3])
            raise ValueError(f"Nenhum lançamento foi identificado. {reasons}")
        self._exporter.export(result, output_path)
        return result
