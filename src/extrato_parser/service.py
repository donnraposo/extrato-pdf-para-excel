"""Fachada compatível para o caso de uso de conversão."""

from pathlib import Path

from .application.use_cases import ConvertStatement
from .domain.entities import ParseResult
from .infrastructure.excel import OpenpyxlStatementExporter
from .infrastructure.pdf import PdfPlumberStatementReader
from .layouts.layout_statement_interpreter import LayoutStatementInterpreter


def convert_statement(pdf_path: Path, output_path: Path) -> ParseResult:
    use_case = ConvertStatement(PdfPlumberStatementReader(), LayoutStatementInterpreter(), OpenpyxlStatementExporter())
    return use_case.execute(pdf_path, output_path)
