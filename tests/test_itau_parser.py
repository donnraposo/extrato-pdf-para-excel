from pathlib import Path
from decimal import Decimal

from extrato_parser.models import PhysicalLine, Word
from extrato_parser.parser import parse_lines


def line(page, top, items):
    words = [Word(text, x, x + max(len(text) * 4, 10), top, top + 8, page) for text, x in items]
    return PhysicalLine(words, page, top)


def test_itau_header_drives_dynamic_schema_and_grouped_dates():
    lines = [
        line(1, 10, [("extrato mensal", 20), ("jan 2026", 100)]),
        line(1, 50, [("data", 10), ("descrição", 90), ("entradas R$", 310), ("saídas R$", 410), ("saldo R$", 550)]),
        line(1, 58, [("(créditos)", 310), ("(débitos)", 410)]),
        line(1, 66, [("C = crédito a compensar", 10)]),
        line(1, 72, [("31/12", 10), ("Saldo anterior", 90), ("62.003,79", 550)]),
        line(1, 90, [("02/01", 10), ("Tar/Custas Cobrança", 90), ("14,29-", 410)]),
        line(1, 102, [("Sispag FERREIRA COSTA", 90), ("2.990,00", 310)]),
        line(1, 114, [("Tar Negat Ent", 90), ("11,81-", 410), ("70.947,69", 550)]),
        line(1, 126, [("Saldo final", 90), ("70.947,69", 550)]),
        line(1, 138, [("Custo efetivo total CET", 90), ("611,42", 310)]),
    ]
    result = parse_lines(lines, Path("itau.pdf"), 1)
    assert result.metadata["Banco provável"] == "Itau"
    assert result.output_fields == ["date", "description", "credit", "debit", "movement", "balance"]
    assert result.field_labels["credit"] == "Entradas (R$)"
    assert result.field_labels["debit"] == "Saídas (R$)"
    assert len(result.entries) == 3
    assert all(entry.transaction_date.isoformat() == "2026-01-02" for entry in result.entries)
    assert result.entries[0].debit > 0 and result.entries[0].movement < 0
    assert result.entries[1].credit > 0 and result.entries[1].movement > 0
    assert result.entries[2].balance == Decimal("70947.69")
    assert "Saldo anterior" not in " ".join(entry.description for entry in result.entries)
