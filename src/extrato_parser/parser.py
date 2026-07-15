from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .models import ParseResult, PhysicalLine, StatementEntry
from .normalization import find_money, parse_brazilian_money, parse_statement_date, plain_text


DATE_TOKEN_RE = re.compile(r"^\d{1,2}/\d{1,2}(?:/\d{2,4})?$")
YEAR_RE = re.compile(r"(?:20)?(\d{2})")


@dataclass
class Columns:
    description: float
    document: float
    credit: float
    debit: float
    balance: float
    header_bottom: float


def _word_x(line: PhysicalLine, *needles: str) -> float | None:
    normalized_needles = tuple(plain_text(item) for item in needles)
    for word in line.words:
        text = plain_text(word.text)
        if any(needle in text for needle in normalized_needles):
            return word.x0
    return None


def _is_header(line: PhysicalLine) -> bool:
    text = plain_text(line.text)
    return "DATA" in text and ("DESCRICAO" in text or "HISTORICO" in text) and "SALDO" in text


def _detect_columns(header: PhysicalLine, next_lines: list[PhysicalLine]) -> Columns:
    description = _word_x(header, "DESCRICAO", "HISTORICO", "LANCAMENTO") or 70.0
    document = _word_x(header, "DOCUMENTO", "DOC") or 290.0
    movement = _word_x(header, "MOVIMENT", "VALOR") or 385.0
    balance = _word_x(header, "SALDO") or 505.0
    credit = movement
    debit = movement + max((balance - movement) / 2, 35.0)
    bottom = max(word.bottom for word in header.words)
    for line in next_lines[:3]:
        if line.page != header.page or line.top - header.top > 30:
            break
        credit_x = _word_x(line, "CREDIT")
        debit_x = _word_x(line, "DEBIT")
        if credit_x is not None:
            credit = credit_x
            bottom = max(bottom, max(word.bottom for word in line.words))
        if debit_x is not None:
            debit = debit_x
            bottom = max(bottom, max(word.bottom for word in line.words))
    return Columns(description, document, credit, debit, balance, bottom)


def _bucket(line: PhysicalLine, columns: Columns) -> dict[str, str]:
    boundaries = [
        (columns.description + columns.document) / 2,
        (columns.document + columns.credit) / 2,
        (columns.credit + columns.debit) / 2,
        (columns.debit + columns.balance) / 2,
    ]
    result: dict[str, list[str]] = {key: [] for key in ("date", "description", "document", "credit", "debit", "balance")}
    for word in line.words:
        center = (word.x0 + word.x1) / 2
        if center < columns.description:
            key = "date"
        elif center < boundaries[0]:
            key = "description"
        elif center < boundaries[1]:
            key = "document"
        elif center < boundaries[2]:
            key = "credit"
        elif center < boundaries[3]:
            key = "debit"
        else:
            key = "balance"
        result[key].append(word.text)
    return {key: " ".join(value).strip() for key, value in result.items()}


def _document_value(text: str) -> str | None:
    cleaned = text.strip()
    return None if not cleaned or cleaned == "-" else cleaned


def _is_trailing_detail(description: str) -> bool:
    """Recognize Santander-like details printed below their movement row."""
    text = plain_text(description).strip()
    if not text:
        return False
    return bool(
        re.match(r"^(PARC(?:ELA)?\b|PERIODO\b|\d{2,}/\d+|CPF\b|CNPJ\b)", text)
        or re.fullmatch(r"[\d./-]+", text)
    )


def _infer_year(lines: list[PhysicalLine]) -> int | None:
    month_names = "JANEIRO|FEVEREIRO|MARCO|ABRIL|MAIO|JUNHO|JULHO|AGOSTO|SETEMBRO|OUTUBRO|NOVEMBRO|DEZEMBRO"
    pattern = re.compile(rf"(?:{month_names})\s*(?:/|DE)?\s*(20\d{{2}})", re.IGNORECASE)
    for line in lines[:60]:
        match = pattern.search(plain_text(line.text))
        if match:
            return int(match.group(1))
    return None


def _bank_name(lines: list[PhysicalLine]) -> str:
    sample = plain_text(" ".join(line.text for line in lines[:40]))
    for bank in ("SANTANDER", "ITAU", "BRADESCO", "CAIXA", "BANCO DO BRASIL", "NUBANK", "SICOOB", "SICREDI"):
        if bank in sample:
            return bank.title()
    return "Desconhecido"


def parse_lines(lines: list[PhysicalLine], source: Path, page_count: int) -> ParseResult:
    result = ParseResult(source=source)
    result.metadata.update({"Páginas": page_count, "Banco provável": _bank_name(lines)})
    default_year = _infer_year(lines)
    if default_year:
        result.metadata["Ano inferido"] = default_year

    columns_by_page: dict[int, Columns] = {}
    for index, line in enumerate(lines):
        if _is_header(line):
            columns_by_page[line.page] = _detect_columns(line, lines[index + 1 :])

    if not columns_by_page:
        result.rejected_lines.append((1, "", "Cabeçalho tabular não identificado"))
        return result

    current_date: date | None = None
    pending_description: list[str] = []
    pending_source: list[str] = []
    pending_document: str | None = None
    pending_page = 1

    def flush_without_value(reason: str) -> None:
        nonlocal pending_description, pending_source, pending_document
        if pending_description:
            result.rejected_lines.append((pending_page, " | ".join(pending_source), reason))
        pending_description = []
        pending_source = []
        pending_document = None

    for line in lines:
        columns = columns_by_page.get(line.page)
        if columns is None or line.top <= columns.header_bottom:
            continue
        normalized = plain_text(line.text)
        if _is_header(line) or normalized.startswith("PAGINA:") or "EXTRATO CONSOLIDADO" in normalized:
            continue
        if normalized.startswith("SALDO EM"):
            flush_without_value("Texto de saldo sem movimento associado")
            continue

        cells = _bucket(line, columns)
        date_text = cells["date"].split()[0] if cells["date"] else ""
        parsed_date = parse_statement_date(date_text, default_year) if DATE_TOKEN_RE.match(date_text) else None
        if parsed_date:
            current_date = parsed_date

        description = cells["description"].strip()
        document = _document_value(cells["document"])
        credit_text = find_money(cells["credit"])
        debit_text = find_money(cells["debit"])
        balance_text = find_money(cells["balance"])
        movement = None
        warnings: list[str] = []
        if credit_text and debit_text:
            warnings.append("Crédito e débito identificados na mesma linha")
        elif credit_text:
            movement = parse_brazilian_money(credit_text)
        elif debit_text:
            movement = parse_brazilian_money(debit_text, debit=True)

        if parsed_date and pending_description:
            flush_without_value("Novo grupo de data antes de encontrar movimento")

        if movement is not None:
            combined_description = " ".join([*pending_description, description]).strip()
            if not combined_description:
                warnings.append("Descrição não identificada")
            if current_date is None:
                warnings.append("Data não identificada")
            balance = parse_brazilian_money(balance_text) if balance_text else None
            credit = parse_brazilian_money(credit_text) if credit_text else None
            parsed_debit = parse_brazilian_money(debit_text) if debit_text else None
            debit = abs(parsed_debit) if parsed_debit is not None else None
            result.entries.append(
                StatementEntry(
                    transaction_date=current_date,
                    description=combined_description,
                    document_number=document or pending_document,
                    movement=movement,
                    balance=balance,
                    page=line.page,
                    source_text=" | ".join([*pending_source, line.text]),
                    credit=credit,
                    debit=debit,
                    warnings=warnings,
                )
            )
            pending_description = []
            pending_source = []
            pending_document = None
        elif balance_text and (description or document):
            result.rejected_lines.append((line.page, line.text, "Saldo encontrado sem movimento"))
        elif description or document:
            if result.entries and _is_trailing_detail(description):
                entry = result.entries[-1]
                if description:
                    entry.description = f"{entry.description} {description}".strip()
                if document and not entry.document_number:
                    entry.document_number = document
                entry.source_text = f"{entry.source_text} | {line.text}".strip(" |")
            else:
                if description:
                    pending_description.append(description)
                if document:
                    pending_document = document
                pending_source.append(line.text)
                pending_page = line.page

    flush_without_value("Fim do documento antes de encontrar movimento")
    result.metadata["Lançamentos identificados"] = len(result.entries)
    result.metadata["Itens para conferência"] = sum(entry.needs_review for entry in result.entries) + len(result.rejected_lines)
    return result


def parse_pdf(path: Path) -> ParseResult:
    from .extraction import extract_pdf_lines

    lines, page_count = extract_pdf_lines(path)
    return parse_lines(lines, path, page_count)
