from datetime import date
from decimal import Decimal
from pathlib import Path

from openpyxl import load_workbook

from extrato_parser.exporter import export_to_excel
from extrato_parser.models import ParseResult, StatementEntry


def test_excel_has_expected_sheets_and_numeric_values(tmp_path):
    result = ParseResult(Path("origem.pdf"))
    result.entries.append(StatementEntry(date(2026, 2, 5), "PIX", None, Decimal("100.50"), None, 1, "PIX"))
    output = tmp_path / "saida.xlsx"
    export_to_excel(result, output)
    workbook = load_workbook(output)
    assert workbook.sheetnames == ["Lançamentos", "Conferência", "Metadados"]
    assert workbook["Lançamentos"]["F2"].value == 100.5
    assert workbook["Lançamentos"]["D1"].value == "Crédito (R$)"
    assert workbook["Lançamentos"]["E1"].value == "Débito (R$)"
