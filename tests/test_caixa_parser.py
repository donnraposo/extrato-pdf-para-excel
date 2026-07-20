from decimal import Decimal
from pathlib import Path

from extrato_parser.models import PhysicalLine, Word
from extrato_parser.parser import parse_lines


def line(page, top, text):
    return PhysicalLine([Word(text, 10, 10 + max(len(text) * 4, 10), top, top + 8, page)], page, top)


def test_caixa_multiline_effective_date_balance_sign_and_page_headers():
    lines = [
        line(1, 10, "Extrato no período de 01/01/2026 à 31/01/2026"),
        line(1, 20, "Data"),
        line(1, 27, "Documento Histórico Valor Saldo"),
        line(1, 34, "Data Efetiva"),
        line(1, 50, "PIX RECEBIDO"),
        line(1, 58, "05/01/2026"),
        line(1, 64, "051452 BEZERROS COMERCIO LTDA R$ 2.625,00 R$ 15.187,34 D"),
        line(1, 72, "05/01 14:52"),
        line(1, 78, "E60746948202601051752C2530Dq7SMM"),
        line(1, 90, "05/01/2026 SALDO DIA R$ 15.187,34 D"),
        line(1, 105, "DEB PIX CHAVE"),
        line(1, 113, "07/01/2026"),
        line(1, 119, "071605 NAGA SOLUCOES LTDA - R$ 7.000,00 R$ 13.204,78 D"),
        line(1, 127, "07/01 16:05"),
        line(1, 133, "E00360305202601071905f92db3a358a"),
        line(1, 150, "about:blank 1/2"),
        line(2, 10, "Data"),
        line(2, 17, "Documento Histórico Valor Saldo"),
        line(2, 24, "Data Efetiva"),
        line(2, 40, "PIX RECEBIDO"),
        line(2, 48, "02/02/2026"),
        line(2, 54, "021331 CLIENTE LTDA R$ 10.476,05 R$ 10.531,74 C"),
        line(2, 62, "02/02 13:31"),
        line(2, 68, "E003603052026020216318097937f06a"),
        line(2, 85, "SAC CAIXA Ouvidoria"),
    ]

    result = parse_lines(lines, Path("caixa.pdf"), 2)

    assert result.metadata["Banco provável"] == "Caixa"
    assert result.output_fields[:4] == ["date", "effective_date", "document", "description"]
    assert result.output_fields == ["date", "effective_date", "document", "description", "movement", "balance"]
    assert result.field_labels["movement"] == "Valor (R$)"
    assert len(result.entries) == 4
    assert result.entries[0].transaction_date.isoformat() == "2026-01-05"
    assert result.entries[0].effective_date.isoformat() == "2026-01-05T14:52:00"
    assert result.entries[0].document_number == "051452"
    assert result.entries[0].movement == Decimal("2625.00")
    assert result.entries[0].balance == "15.187,34 D"
    assert "PIX RECEBIDO" in result.entries[0].description
    assert "E607469" in result.entries[0].description
    assert result.entries[1].description == "SALDO DIA"
    assert result.entries[1].balance == "15.187,34 D"
    assert result.entries[1].movement is None
    assert not result.entries[1].needs_review
    assert result.entries[2].debit == Decimal("7000.00")
    assert result.entries[3].balance == "10.531,74 C"
    assert "Data fora do período informado no extrato" in result.entries[3].warnings
