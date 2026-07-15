from decimal import Decimal

from extrato_parser.normalization import parse_brazilian_money, parse_statement_date


def test_brazilian_money_credit_and_debit():
    assert parse_brazilian_money("1.368,50") == Decimal("1368.50")
    assert parse_brazilian_money("335,99-") == Decimal("-335.99")
    assert parse_brazilian_money("335,99", debit=True) == Decimal("-335.99")


def test_statement_date_uses_default_year():
    assert parse_statement_date("05/02", 2026).isoformat() == "2026-02-05"
    assert parse_statement_date("31/02", 2026) is None
