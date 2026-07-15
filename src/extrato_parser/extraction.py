from __future__ import annotations

from pathlib import Path

import pdfplumber

from .models import PhysicalLine, Word


class PdfTextError(RuntimeError):
    pass


def group_words_into_lines(words: list[Word], tolerance: float = 3.0) -> list[PhysicalLine]:
    lines: list[PhysicalLine] = []
    for word in sorted(words, key=lambda item: (item.page, item.top, item.x0)):
        target = next(
            (
                line
                for line in reversed(lines)
                if line.page == word.page and abs(line.top - word.top) <= tolerance
            ),
            None,
        )
        if target is None:
            lines.append(PhysicalLine([word], word.page, word.top))
        else:
            target.words.append(word)
            target.top = sum(item.top for item in target.words) / len(target.words)
    for line in lines:
        line.words.sort(key=lambda item: item.x0)
    return lines


def extract_pdf_lines(path: Path) -> tuple[list[PhysicalLine], int]:
    all_lines: list[PhysicalLine] = []
    pages_with_text = 0
    try:
        with pdfplumber.open(path) as document:
            page_count = len(document.pages)
            for page_number, page in enumerate(document.pages, start=1):
                raw_words = page.extract_words(
                    x_tolerance=2,
                    y_tolerance=2,
                    keep_blank_chars=False,
                    use_text_flow=False,
                )
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
                all_lines.extend(group_words_into_lines(words))
    except Exception as exc:
        raise PdfTextError(f"Não foi possível ler o PDF: {exc}") from exc

    if not all_lines or pages_with_text == 0:
        raise PdfTextError(
            "O PDF não possui texto selecionável. A versão atual ainda não utiliza OCR."
        )
    return all_lines, page_count
