from __future__ import annotations

from pathlib import Path

from .exporter import export_to_excel
from .models import ParseResult
from .parser import parse_pdf


def convert_statement(pdf_path: Path, output_path: Path) -> ParseResult:
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Selecione um arquivo PDF.")
    if not pdf_path.is_file():
        raise FileNotFoundError("O arquivo PDF selecionado não existe.")
    if output_path.suffix.lower() != ".xlsx":
        output_path = output_path.with_suffix(".xlsx")
    result = parse_pdf(pdf_path)
    if not result.entries and result.rejected_lines:
        reasons = "; ".join(item[2] for item in result.rejected_lines[:3])
        raise ValueError(f"Nenhum lançamento foi identificado. {reasons}")
    export_to_excel(result, output_path)
    return result
