from decimal import Decimal
from pathlib import Path

from extrato_parser.models import PhysicalLine, Word
from extrato_parser.parser import parse_lines


def line(page, top, items):
    words = [Word(text, x, x + max(len(text) * 4, 10), top, top + 8, page) for text, x in items]
    return PhysicalLine(words, page, top)


def test_inter_grouped_dates_signed_values_and_transaction_balance():
    lines = [
        line(1, 10, [("Saldo total", 10), ("R$ 1,01", 10)]),
        line(1, 50, [("6 de Janeiro de 2026 Saldo do dia: R$ 0,82", 10), ("Valor", 390), ("Saldo por transação", 500)]),
        line(1, 85, [("Pagamento efetuado: 'Pagamento fatura cartão Inter'", 10), ("-R$ 1.000,00", 390), ("-R$ 999,18", 500)]),
        line(1, 100, [("Pix recebido: 'Ctp 60701190-NAGA SOLUCOES LTDA'", 10), ("R$ 1.000,00", 390), ("R$ 0,82", 500)]),
        line(1, 120, [("20 de Janeiro de 2026 Saldo do dia: R$ 814,24", 10)]),
        line(1, 135, [("Aplicação: 'CDB OBJ PJ BANCO INTER S A'", 10), ("-R$ 42,76", 390), ("-R$ 41,09", 500)]),
        line(1, 150, [("Crédito domicílio cartão: 'ANTECIPACAO - INTER PAG'", 10), ("R$ 855,33", 390), ("R$ 814,24", 500)]),
        line(1, 170, [("Fale com a gente", 10)]),
        line(1, 185, [("SAC: 0800 940 9999", 10), ("R$ 99,00", 390)]),
    ]

    result = parse_lines(lines, Path("inter.pdf"), 1)

    assert result.metadata["Banco provável"] == "Inter"
    assert result.output_fields == ["date", "description", "credit", "debit", "movement", "balance"]
    assert len(result.entries) == 4
    assert result.entries[0].transaction_date.isoformat() == "2026-01-06"
    assert result.entries[0].movement == Decimal("-1000.00")
    assert result.entries[0].debit == Decimal("1000.00")
    assert result.entries[0].balance == Decimal("-999.18")
    assert result.entries[1].credit == Decimal("1000.00")
    assert result.entries[2].transaction_date.isoformat() == "2026-01-20"
    assert result.entries[3].balance == Decimal("814.24")


def test_inter_uses_text_values_when_pdf_coordinates_are_unreliable():
    lines = [
        line(1, 50, [("6 de Janeiro de 2026 Saldo do dia: R$ 0,82 Valor Saldo por transação", 10)]),
        line(1, 80, [("Pagamento efetuado: \"Pagamento fatura cartao Inter\" -R$ 1.000,00 -R$ 999,18", 10)]),
        line(1, 95, [("Pix recebido: \"Cp :60701190-NAGA SOLUCOES LTDA\" R$ 1.000,00 R$ 0,82", 10)]),
    ]

    result = parse_lines(lines, Path("inter-texto.pdf"), 1)

    assert len(result.entries) == 2
    assert all(entry.transaction_date.isoformat() == "2026-01-06" for entry in result.entries)
    assert result.entries[0].description == 'Pagamento efetuado: "Pagamento fatura cartao Inter"'
    assert result.entries[0].movement == Decimal("-1000.00")
    assert result.entries[0].balance == Decimal("-999.18")
    assert result.entries[1].movement == Decimal("1000.00")
    assert result.entries[1].balance == Decimal("0.82")


def test_inter_complete_sample_has_all_sixteen_entries():
    texts = [
        "6 de Janeiro de 2026 Saldo do dia: R$ 0,82 Valor Saldo por transação",
        'Pagamento efetuado: "Pagamento fatura cartao Inter" -R$ 1.000,00 -R$ 999,18',
        'Pix recebido: "Cp :60701190-NAGA SOLUCOES LTDA" R$ 1.000,00 R$ 0,82',
        "8 de Janeiro de 2026 Saldo do dia: R$ 0,82",
        'Pagamento efetuado: "Pagamento fatura cartao Inter" -R$ 1.000,00 -R$ 999,18',
        'Pix recebido: "Cp :60701190-NAGA SOLUCOES LTDA" R$ 1.000,00 R$ 0,82',
        "12 de Janeiro de 2026 Saldo do dia: R$ 1,67",
        'Pagamento efetuado: "Pagamento fatura cartao Inter" -R$ 2.282,15 -R$ 2.281,33',
        'Pix recebido: "Cp :60701190-NAGA SOLUCOES LTDA" R$ 2.283,00 R$ 1,67',
        "16 de Janeiro de 2026 Saldo do dia: R$ 1,67",
        'Pagamento efetuado: "Pagamento fatura cartao Inter" -R$ 1.000,00 -R$ 998,33',
        'Pix recebido: "Cp :60701190-NAGA SOLUCOES LTDA" R$ 1.000,00 R$ 1,67',
        "20 de Janeiro de 2026 Saldo do dia: R$ 814,24",
        'Aplicacao: "CDB OBJ PJ BANCO INTER S A" -R$ 42,76 -R$ 41,09',
        'Credito domicilio cartao: "ANTECIPACAO - INTER PAG" R$ 855,33 R$ 814,24',
        "21 de Janeiro de 2026 Saldo do dia: R$ 0,24",
        'Pagamento efetuado: "Pagamento fatura cartao Inter" -R$ 814,00 R$ 0,24',
        "22 de Janeiro de 2026 Saldo do dia: R$ 51,85",
        'Aplicacao: "CDB OBJ PJ BANCO INTER S A" -R$ 2,71 -R$ 2,47',
        'Credito domicilio cartao: "CARTAO DE DEBITO - INTER PAG" R$ 54,32 R$ 51,85',
        "23 de Janeiro de 2026 Saldo do dia: R$ 0,05",
        'Pix enviado: "Cp :60701190-Fernando Henrique Pinto" -R$ 504,00 -R$ 452,15',
        'Resgate: "CDB OBJ PJ BANCO INTER S A" R$ 133,33 -R$ 318,82',
        'Resgate: "CDB OBJ PJ BANCO INTER S A" R$ 18,98 -R$ 299,84',
    ]
    lines = [line(1, 50 + index * 10, [(text, 10)]) for index, text in enumerate(texts)]

    result = parse_lines(lines, Path("inter-amostra-completa.pdf"), 1)

    assert len(result.entries) == 16
    assert not result.rejected_lines
    assert result.entries[-1].transaction_date.isoformat() == "2026-01-23"
    assert result.entries[-1].credit == Decimal("18.98")
    assert result.entries[-1].balance == Decimal("-299.84")
