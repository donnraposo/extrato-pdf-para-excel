from pathlib import Path

from extrato_parser.models import PhysicalLine, Word
from extrato_parser.parser import parse_lines


def line(page, top, items):
    words = [Word(text, x, x + max(len(text) * 5, 10), top, top + 8, page) for text, x in items]
    return PhysicalLine(words, page, top)


def test_santander_like_multiline_and_signs():
    lines = [
        line(1, 10, [("fevereiro/2026", 30)]),
        line(1, 50, [("Data", 30), ("Descrição", 70), ("Nº Documento", 290), ("Movimentos", 385), ("Saldo", 505)]),
        line(1, 60, [("Créditos", 385), ("Débitos", 445)]),
        line(1, 80, [("05/02", 30), ("A CR COB RECEBIMENTO", 70), ("335,99", 390)]),
        line(1, 86, [("3749/000111486", 70)]),
        line(1, 92, [("PREST. DE EMPREST.", 70)]),
        line(1, 104, [("PARC 003/022", 70), ("025960", 295), ("335,99-", 450), ("0,00", 510)]),
        line(1, 110, [("PERIODO: 01/02 A 04/02/26", 70)]),
    ]
    result = parse_lines(lines, Path("amostra.pdf"), 1)
    assert len(result.entries) == 2
    assert result.entries[0].movement > 0
    assert result.entries[0].credit > 0
    assert result.entries[0].debit is None
    assert "3749/000111486" in result.entries[0].description
    assert result.entries[1].movement < 0
    assert result.entries[1].credit is None
    assert result.entries[1].debit > 0
    assert result.entries[1].document_number == "025960"
    assert result.entries[1].balance == 0
    assert "PREST. DE EMPREST." in result.entries[1].description
    assert "PERIODO:" in result.entries[1].description
