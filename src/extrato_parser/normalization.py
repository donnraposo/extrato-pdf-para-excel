from __future__ import annotations

import re
import unicodedata
from datetime import date
from decimal import Decimal, InvalidOperation


MONEY_RE = re.compile(r"(?<!\d)(\d{1,3}(?:\.\d{3})*|\d+),\d{2}-?(?!\d)")
DATE_RE = re.compile(r"^(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?$")


def plain_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char)).upper()


def parse_brazilian_money(value: str, *, debit: bool = False) -> Decimal | None:
    cleaned = value.strip().replace("R$", "").replace(" ", "")
    negative = debit or cleaned.endswith("-") or cleaned.startswith("-")
    cleaned = cleaned.strip("-").replace(".", "").replace(",", ".")
    if not cleaned:
        return None
    try:
        number = Decimal(cleaned)
    except InvalidOperation:
        return None
    return -abs(number) if negative else abs(number)


def parse_statement_date(value: str, default_year: int | None) -> date | None:
    match = DATE_RE.match(value.strip())
    if not match:
        return None
    day, month = int(match.group(1)), int(match.group(2))
    year_text = match.group(3)
    if year_text:
        year = int(year_text)
        if year < 100:
            year += 2000
    elif default_year:
        year = default_year
    else:
        return None
    try:
        return date(year, month, day)
    except ValueError:
        return None


def find_money(text: str) -> str | None:
    matches = MONEY_RE.findall(text)
    if not matches:
        return None
    # findall omits the optional trailing sign because of the capture group.
    full = list(MONEY_RE.finditer(text))[-1].group(0)
    return full
