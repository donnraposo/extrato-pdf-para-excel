from pathlib import Path

import pdfplumber

from ...application.ports import StatementReader
from ...domain.entities import PhysicalLine, Word
from .pdf_text_error import PdfTextError
from .word_line_grouper import WordLineGrouper


class PdfPlumberStatementReader(StatementReader):
    def __init__(self, grouper: WordLineGrouper | None = None) -> None:
        self._grouper = grouper or WordLineGrouper()

    def read(self, path: Path) -> tuple[list[PhysicalLine], int]:
        all_lines: list[PhysicalLine] = []
        pages_with_text = 0
        try:
            with pdfplumber.open(path) as document:
                page_count = len(document.pages)
                for page_number, page in enumerate(document.pages, start=1):
                    raw_words = page.extract_words(x_tolerance=2, y_tolerance=2, keep_blank_chars=False, use_text_flow=False)
                    words = [
                        Word(
                            text=item["text"],
                            x0=float(item["x0"]),
                            x1=float(item["x1"]),
                            top=float(item["top"]),
                            bottom=float(item["bottom"]),
                            page=page_number,
                        )
                        for item in raw_words
                        if item.get("text", "").strip()
                    ]
                    if words:
                        pages_with_text += 1
                    all_lines.extend(self._grouper.group(words))
        except Exception as exc:
            raise PdfTextError(f"Não foi possível ler o PDF: {exc}") from exc
        if not all_lines or pages_with_text == 0:
            raise PdfTextError("O PDF não possui texto selecionável. A versão atual ainda não utiliza OCR.")
        return all_lines, page_count
