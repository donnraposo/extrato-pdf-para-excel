"""Fachada compatível para a infraestrutura de leitura de PDF."""

from pathlib import Path

from .domain.entities import PhysicalLine, Word
from .infrastructure.pdf import PdfPlumberStatementReader, PdfTextError, WordLineGrouper


def group_words_into_lines(words: list[Word], tolerance: float = 3.0) -> list[PhysicalLine]:
    return WordLineGrouper(tolerance).group(words)


def extract_pdf_lines(path: Path) -> tuple[list[PhysicalLine], int]:
    return PdfPlumberStatementReader().read(path)


__all__ = ["PdfTextError", "extract_pdf_lines", "group_words_into_lines"]
