from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

from .models import ParseResult, PhysicalLine, StatementEntry
from .normalization import find_money, parse_brazilian_money, parse_statement_date, plain_text
from .layouts.generic.columns import Columns


DATE_TOKEN_RE = re.compile(r"^\d{1,2}/\d{1,2}(?:/\d{2,4})?$")
YEAR_RE = re.compile(r"(?:20)?(\d{2})")
INTER_DATE_RE = re.compile(
    r"^(\d{1,2}) DE (JANEIRO|FEVEREIRO|MARCO|ABRIL|MAIO|JUNHO|JULHO|AGOSTO|SETEMBRO|OUTUBRO|NOVEMBRO|DEZEMBRO) DE (20\d{2})\b"
)
INTER_MONEY_RE = re.compile(r"-?\s*R\$\s*\d{1,3}(?:\.\d{3})*,\d{2}")
CAIXA_FULL_DATE_RE = re.compile(r"\b\d{2}/\d{2}/20\d{2}\b")
CAIXA_EFFECTIVE_RE = re.compile(r"\b(\d{2})/(\d{2})\s+(\d{2}):(\d{2})\b")
CAIXA_DOCUMENT_RE = re.compile(r"\b\d{6}\b")
INTER_MONTHS = {
    name: month
    for month, name in enumerate(
        ("JANEIRO", "FEVEREIRO", "MARCO", "ABRIL", "MAIO", "JUNHO", "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"),
        start=1,
    )
}


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
    document = _word_x(header, "DOCUMENTO", "N DOC")
    movement = _word_x(header, "MOVIMENT", "VALOR") or 385.0
    balance = _word_x(header, "SALDO") or 505.0
    header_credit = _word_x(header, "ENTRADA", "CREDITO")
    header_debit = _word_x(header, "SAIDA", "DEBITO")
    credit = header_credit if header_credit is not None else movement
    debit = header_debit if header_debit is not None else movement + max((balance - movement) / 2, 35.0)
    credit_label = "Entradas (R$)" if _word_x(header, "ENTRADA") is not None else "Crédito (R$)"
    debit_label = "Saídas (R$)" if _word_x(header, "SAIDA") is not None else "Débito (R$)"
    bottom = max(word.bottom for word in header.words)
    for line in next_lines[:3]:
        if line.page != header.page or line.top - header.top > 30:
            break
        credit_x = _word_x(line, "CREDIT")
        debit_x = _word_x(line, "DEBIT")
        # Itaú prints a legend (for example "C = crédito a compensar")
        # below the header. Only accept subheaders inside the tabular region.
        if credit_x is not None and description < credit_x < balance:
            credit = credit_x
            bottom = max(bottom, max(word.bottom for word in line.words))
        if debit_x is not None and description < debit_x < balance:
            debit = debit_x
            bottom = max(bottom, max(word.bottom for word in line.words))
    return Columns(description, document, credit, debit, balance, bottom, credit_label, debit_label)


def _bucket(line: PhysicalLine, columns: Columns) -> dict[str, str]:
    description_end = (
        (columns.description + columns.document) / 2
        if columns.document is not None
        else (columns.description + columns.credit) / 2
    )
    document_end = (
        (columns.document + columns.credit) / 2
        if columns.document is not None
        else description_end
    )
    credit_end = (columns.credit + columns.debit) / 2
    debit_end = (columns.debit + columns.balance) / 2
    result: dict[str, list[str]] = {key: [] for key in ("date", "description", "document", "credit", "debit", "balance")}
    for word in line.words:
        center = (word.x0 + word.x1) / 2
        if center < columns.description:
            key = "date"
        elif center < description_end:
            key = "description"
        elif columns.document is not None and center < document_end:
            key = "document"
        elif center < credit_end:
            key = "credit"
        elif center < debit_end:
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
    month_names = (
        "JAN(?:EIRO)?|FEV(?:EREIRO)?|MAR(?:CO)?|ABR(?:IL)?|MAI(?:O)?|JUN(?:HO)?|"
        "JUL(?:HO)?|AGO(?:STO)?|SET(?:EMBRO)?|OUT(?:UBRO)?|NOV(?:EMBRO)?|DEZ(?:EMBRO)?"
    )
    pattern = re.compile(rf"(?:{month_names})\s*(?:/|DE)?\s*(20\d{{2}})", re.IGNORECASE)
    for line in lines[:60]:
        match = pattern.search(plain_text(line.text))
        if match:
            return int(match.group(1))
    return None


def _bank_name(lines: list[PhysicalLine]) -> str:
    sample = plain_text(" ".join(line.text for line in lines[:40]))
    for bank in ("SANTANDER", "ITAU", "BANCO INTER", "BRADESCO", "CAIXA", "BANCO DO BRASIL", "NUBANK", "SICOOB", "SICREDI"):
        if bank in sample:
            return "Inter" if bank == "BANCO INTER" else bank.title()
    return "Desconhecido"


def _is_inter_header(line: PhysicalLine) -> bool:
    text = plain_text(line.text)
    return "VALOR" in text and "SALDO POR TRANSACAO" in text


def _is_caixa_layout(lines: list[PhysicalLine]) -> bool:
    texts = [plain_text(line.text) for line in lines]
    has_columns = any("DOCUMENTO" in text and "HISTORICO" in text and "VALOR" in text and "SALDO" in text for text in texts)
    has_effective_date = any(text.strip() == "DATA EFETIVA" for text in texts)
    has_caixa_signature = any("SAC CAIXA" in text for text in texts) or any("SALDO DIA" in text for text in texts)
    return has_columns and has_effective_date and has_caixa_signature


def _caixa_period(lines: list[PhysicalLine]) -> tuple[date, date] | None:
    pattern = re.compile(r"EXTRATO NO PERIODO DE (\d{2}/\d{2}/20\d{2}) A (\d{2}/\d{2}/20\d{2})")
    for line in lines:
        match = pattern.search(plain_text(line.text))
        if match:
            start = parse_statement_date(match.group(1), None)
            end = parse_statement_date(match.group(2), None)
            if start and end:
                return start, end
    return None


def _parse_caixa_effective(value: str, year: int) -> datetime | None:
    match = CAIXA_EFFECTIVE_RE.search(value)
    if not match:
        return None
    try:
        return datetime(year, int(match.group(2)), int(match.group(1)), int(match.group(3)), int(match.group(4)))
    except ValueError:
        return None


def _caixa_balance_text(line_text: str, money_match: re.Match[str]) -> str:
    number = money_match.group(0).replace("R$", "").replace(" ", "").lstrip("-")
    suffix_match = re.search(r"\b([CD])\b", plain_text(line_text[money_match.end() :]))
    return f"{number} {suffix_match.group(1)}" if suffix_match else number


def _is_caixa_ignored_line(text: str) -> bool:
    normalized = plain_text(text).strip()
    return bool(
        not normalized
        or normalized in {"DATA", "DATA EFETIVA"}
        or normalized.startswith("DOCUMENTO HISTORICO VALOR SALDO")
        or normalized.startswith("SALDO ANTERIOR AO PERIODO")
        or normalized.startswith("EXTRATO NO PERIODO")
        or "SALDO DIA" in normalized
        or normalized.startswith("ABOUT:BLANK")
        or normalized.endswith("EXTRATO_PDF")
        or normalized.startswith(("SAC CAIXA", "OUVIDORIA", "PESSOAS COM DEFICIENCIA", "ALO CAIXA"))
        or re.fullmatch(r"(?:0800\s+\d+\s+\d+\s*)+", normalized) is not None
    )


def _parse_caixa_lines(lines: list[PhysicalLine], source: Path, page_count: int) -> ParseResult:
    result = ParseResult(source=source)
    period = _caixa_period(lines)
    result.metadata.update({"Páginas": page_count, "Banco provável": "Caixa"})
    if period:
        result.metadata.update({"Período inicial": period[0], "Período final": period[1]})
    result.output_fields = ["date", "effective_date", "document", "description", "movement", "balance"]
    result.field_labels = {
        "date": "Data",
        "effective_date": "Data Efetiva",
        "document": "Documento",
        "description": "Histórico",
        "movement": "Valor (R$)",
        "balance": "Saldo (R$)",
    }

    by_page: dict[int, list[PhysicalLine]] = {}
    for line in lines:
        by_page.setdefault(line.page, []).append(line)

    for page_number, page_lines in by_page.items():
        page_entries: list[tuple[float, StatementEntry]] = []
        header_bottom = max(
            (line.top for line in page_lines if plain_text(line.text).strip() == "DATA EFETIVA"),
            default=float("-inf"),
        )
        candidates = [
            line
            for line in page_lines
            if len(INTER_MONEY_RE.findall(line.text)) >= 2
            and "SALDO DIA" not in plain_text(line.text)
            and "SALDO ANTERIOR" not in plain_text(line.text)
        ]
        for index, value_line in enumerate(candidates):
            lower = (candidates[index - 1].top + value_line.top) / 2 if index else header_bottom
            upper = (value_line.top + candidates[index + 1].top) / 2 if index + 1 < len(candidates) else float("inf")
            segment = [line for line in page_lines if lower < line.top < upper and not _is_caixa_ignored_line(line.text)]

            date_candidates: list[tuple[float, str]] = []
            effective_text: str | None = None
            for segment_line in segment:
                full_date = CAIXA_FULL_DATE_RE.search(segment_line.text)
                if full_date and segment_line.top <= value_line.top + 1:
                    date_candidates.append((segment_line.top, full_date.group(0)))
                effective = CAIXA_EFFECTIVE_RE.search(segment_line.text)
                if effective:
                    effective_text = effective.group(0)
            transaction_date = parse_statement_date(max(date_candidates)[1], None) if date_candidates else None
            effective_date = _parse_caixa_effective(effective_text, transaction_date.year) if effective_text and transaction_date else None

            matches = list(INTER_MONEY_RE.finditer(value_line.text))
            movement_text, balance_text = matches[-2].group(0), matches[-1].group(0)
            movement = parse_brazilian_money(movement_text)
            balance = _caixa_balance_text(value_line.text, matches[-1])

            prefix = value_line.text[: matches[-2].start()]
            document_match = CAIXA_DOCUMENT_RE.search(prefix)
            document = document_match.group(0) if document_match else None
            history_parts: list[str] = []
            for segment_line in segment:
                cleaned = segment_line.text
                cleaned = INTER_MONEY_RE.sub(" ", cleaned)
                cleaned = CAIXA_FULL_DATE_RE.sub(" ", cleaned)
                cleaned = CAIXA_EFFECTIVE_RE.sub(" ", cleaned)
                if segment_line is value_line and document:
                    cleaned = re.sub(rf"\b{re.escape(document)}\b", " ", cleaned, count=1)
                cleaned = re.sub(r"\s+[CD]\s*$", " ", cleaned, flags=re.IGNORECASE)
                cleaned = " ".join(cleaned.split()).strip()
                if cleaned and cleaned not in history_parts and not _is_caixa_ignored_line(cleaned):
                    history_parts.append(cleaned)

            warnings: list[str] = []
            if transaction_date is None:
                warnings.append("Data não identificada")
            if effective_date is None:
                warnings.append("Data efetiva não identificada")
            if document is None:
                warnings.append("Documento não identificado")
            if period and transaction_date and not (period[0] <= transaction_date <= period[1]):
                warnings.append("Data fora do período informado no extrato")
            if movement is None:
                warnings.append("Valor do movimento inválido")

            description = " ".join(history_parts)
            description = re.sub(r"(?<=\d)-\s+(?=\d{2}\b)", "-", description)
            page_entries.append(
                (value_line.top, StatementEntry(
                    transaction_date=transaction_date,
                    effective_date=effective_date,
                    description=description,
                    document_number=document,
                    movement=movement,
                    balance=balance,
                    page=page_number,
                    source_text=" | ".join(line.text for line in segment),
                    credit=movement if movement is not None and movement >= 0 else None,
                    debit=abs(movement) if movement is not None and movement < 0 else None,
                    warnings=warnings,
                ))
            )

        for balance_line in page_lines:
            normalized = plain_text(balance_line.text)
            if "SALDO DIA" not in normalized:
                continue
            date_match = CAIXA_FULL_DATE_RE.search(balance_line.text)
            money_matches = list(INTER_MONEY_RE.finditer(balance_line.text))
            if not date_match or not money_matches:
                result.rejected_lines.append((page_number, balance_line.text, "Saldo do dia incompleto"))
                continue
            balance = _caixa_balance_text(balance_line.text, money_matches[-1])
            page_entries.append(
                (
                    balance_line.top,
                    StatementEntry(
                        transaction_date=parse_statement_date(date_match.group(0), None),
                        effective_date=None,
                        description="SALDO DIA",
                        document_number=None,
                        movement=None,
                        balance=balance,
                        page=page_number,
                        source_text=balance_line.text,
                        balance_only=True,
                    ),
                )
            )
        result.entries.extend(entry for _, entry in sorted(page_entries, key=lambda item: item[0]))

    daily_balance_count = sum(entry.balance_only for entry in result.entries)
    result.metadata["Lançamentos identificados"] = len(result.entries)
    result.metadata["Saldos do dia identificados"] = daily_balance_count
    result.metadata["Itens para conferência"] = sum(entry.needs_review for entry in result.entries) + len(result.rejected_lines)
    return result


def _parse_inter_date(text: str) -> date | None:
    match = INTER_DATE_RE.match(plain_text(text))
    if not match:
        return None
    try:
        return date(int(match.group(3)), INTER_MONTHS[match.group(2)], int(match.group(1)))
    except ValueError:
        return None


def _parse_inter_lines(lines: list[PhysicalLine], source: Path, page_count: int) -> ParseResult:
    result = ParseResult(source=source)
    result.metadata.update({"Páginas": page_count, "Banco provável": "Inter"})
    result.output_fields = ["date", "description", "credit", "debit", "movement", "balance"]
    result.field_labels = {
        "date": "Data",
        "description": "Descrição",
        "credit": "Crédito (R$)",
        "debit": "Débito (R$)",
        "movement": "Movimento (R$)",
        "balance": "Saldo por transação (R$)",
    }

    header_bottom_by_page: dict[int, float] = {}
    for line in lines:
        if not _is_inter_header(line):
            continue
        header_bottom_by_page[line.page] = max(word.bottom for word in line.words)

    current_date: date | None = None
    pending_description: list[str] = []
    stopped_pages: set[int] = set()
    for line in lines:
        header_bottom = header_bottom_by_page.get(line.page)
        if header_bottom is None or line.page in stopped_pages:
            continue
        normalized = plain_text(line.text)
        if normalized.startswith("FALE COM A GENTE"):
            stopped_pages.add(line.page)
            continue
        group_date = _parse_inter_date(line.text)
        if group_date:
            current_date = group_date
            pending_description = []
            continue
        if line.top <= header_bottom or _is_inter_header(line):
            continue

        money_matches = list(INTER_MONEY_RE.finditer(line.text))
        if len(money_matches) >= 2:
            value_match, balance_match = money_matches[-2:]
            description = line.text[: value_match.start()].strip()
            value_text = value_match.group(0)
            balance_text = balance_match.group(0)
            movement = parse_brazilian_money(value_text)
            if movement is None:
                result.rejected_lines.append((line.page, line.text, "Valor do lançamento inválido"))
                continue
            full_description = " ".join([*pending_description, description]).strip()
            warnings: list[str] = []
            if current_date is None:
                warnings.append("Data não identificada")
            if not full_description:
                warnings.append("Descrição não identificada")
            balance = parse_brazilian_money(balance_text)
            result.entries.append(
                StatementEntry(
                    transaction_date=current_date,
                    description=full_description,
                    document_number=None,
                    movement=movement,
                    balance=balance,
                    page=line.page,
                    source_text=line.text,
                    credit=movement if movement >= 0 else None,
                    debit=abs(movement) if movement < 0 else None,
                    warnings=warnings,
                )
            )
            pending_description = []
        elif line.text.strip() and not normalized.startswith(("SALDO TOTAL", "SALDO DISPONIVEL", "SALDO BLOQUEADO")):
            pending_description.append(line.text.strip())

    if pending_description:
        result.rejected_lines.append((page_count, " ".join(pending_description), "Descrição sem valor associado"))
    result.metadata["Lançamentos identificados"] = len(result.entries)
    result.metadata["Itens para conferência"] = sum(entry.needs_review for entry in result.entries) + len(result.rejected_lines)
    return result


def _parse_generic_lines(lines: list[PhysicalLine], source: Path, page_count: int) -> ParseResult:
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

    detected_columns = list(columns_by_page.values())
    has_document = any(columns.document is not None for columns in detected_columns)
    credit_label = next((columns.credit_label for columns in detected_columns if columns.credit_label.startswith("Entradas")), detected_columns[0].credit_label)
    debit_label = next((columns.debit_label for columns in detected_columns if columns.debit_label.startswith("Saídas")), detected_columns[0].debit_label)
    if result.metadata["Banco provável"] == "Desconhecido" and credit_label.startswith("Entradas") and debit_label.startswith("Saídas"):
        result.metadata["Banco provável"] = "Itau"
    result.output_fields = ["date", "description"]
    if has_document:
        result.output_fields.append("document")
    result.output_fields.extend(["credit", "debit", "movement", "balance"])
    result.field_labels = {
        "date": "Data",
        "description": "Descrição",
        "document": "Nº Documento",
        "credit": credit_label,
        "debit": debit_label,
        "movement": "Movimento (R$)",
        "balance": "Saldo (R$)",
    }

    current_date: date | None = None
    pending_description: list[str] = []
    pending_source: list[str] = []
    pending_document: str | None = None
    pending_page = 1
    ended_pages: set[int] = set()

    def flush_without_value(reason: str) -> None:
        nonlocal pending_description, pending_source, pending_document
        if pending_description:
            result.rejected_lines.append((pending_page, " | ".join(pending_source), reason))
        pending_description = []
        pending_source = []
        pending_document = None

    for line in lines:
        columns = columns_by_page.get(line.page)
        if columns is None or line.top <= columns.header_bottom or line.page in ended_pages:
            continue
        normalized = plain_text(line.text)
        if _is_header(line) or normalized.startswith("PAGINA:") or "EXTRATO CONSOLIDADO" in normalized:
            continue
        if normalized.startswith("SALDO EM") or "SALDO ANTERIOR" in normalized:
            flush_without_value("Texto de saldo sem movimento associado")
            continue
        if normalized.startswith("SALDO FINAL"):
            flush_without_value("Fim da região de movimentações")
            ended_pages.add(line.page)
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


def parse_lines(lines: list[PhysicalLine], source: Path, page_count: int) -> ParseResult:
    from .layouts.layout_statement_interpreter import LayoutStatementInterpreter

    return LayoutStatementInterpreter().interpret(lines, source, page_count)


def parse_pdf(path: Path) -> ParseResult:
    from .extraction import extract_pdf_lines

    lines, page_count = extract_pdf_lines(path)
    return parse_lines(lines, path, page_count)
