from __future__ import annotations

from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from .models import ParseResult


COMMON_HEADERS = [
    "Data",
    "Descrição",
    "Nº Documento",
    "Crédito (R$)",
    "Débito (R$)",
    "Movimento (R$)",
    "Saldo (R$)",
]
HEADER_FILL = PatternFill("solid", fgColor="D9EAF7")


def _style_sheet(sheet) -> None:
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.fill = HEADER_FILL
    for column in sheet.columns:
        values = [len(str(cell.value or "")) for cell in column]
        width = min(max(values + [10]) + 2, 60)
        sheet.column_dimensions[get_column_letter(column[0].column)].width = width


def export_to_excel(result: ParseResult, output: Path) -> None:
    workbook = Workbook()
    entries_sheet = workbook.active
    entries_sheet.title = "Lançamentos"
    extra_headers = list(result.detected_extra_fields)
    headers = COMMON_HEADERS + extra_headers + ["Página de origem", "Status"]
    entries_sheet.append(headers)

    for entry in result.entries:
        row = [
            entry.transaction_date,
            entry.description,
            entry.document_number,
            float(entry.credit) if entry.credit is not None else None,
            float(entry.debit) if entry.debit is not None else None,
            float(entry.movement) if entry.movement is not None else None,
            float(entry.balance) if entry.balance is not None else None,
            *[entry.extra_fields.get(name) for name in extra_headers],
            entry.page,
            "Conferir" if entry.needs_review else "OK",
        ]
        entries_sheet.append(row)
        entries_sheet.cell(entries_sheet.max_row, 1).number_format = "dd/mm/yyyy"
        for column in range(4, 8):
            entries_sheet.cell(entries_sheet.max_row, column).number_format = '#,##0.00;[Red]-#,##0.00'
    _style_sheet(entries_sheet)

    review = workbook.create_sheet("Conferência")
    review.append(["Página", "Tipo", "Descrição/Texto original", "Motivo"])
    for entry in result.entries:
        if entry.needs_review:
            review.append([entry.page, "Lançamento", entry.source_text, "; ".join(entry.warnings) or "Dados incompletos"])
    for page, text, reason in result.rejected_lines:
        review.append([page, "Linha não estruturada", text, reason])
    _style_sheet(review)

    metadata = workbook.create_sheet("Metadados")
    metadata.append(["Campo", "Valor"])
    metadata.append(["Arquivo de origem", result.source.name])
    metadata.append(["Processado em", datetime.now().astimezone().isoformat(timespec="seconds")])
    for key, value in result.metadata.items():
        metadata.append([key, value])
    _style_sheet(metadata)

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp.xlsx")
    try:
        workbook.save(temporary)
        temporary.replace(output)
    finally:
        if temporary.exists():
            temporary.unlink()
