from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Word:
    text: str
    x0: float
    x1: float
    top: float
    bottom: float
    page: int


@dataclass
class PhysicalLine:
    words: list[Word]
    page: int
    top: float

    @property
    def text(self) -> str:
        return " ".join(word.text for word in sorted(self.words, key=lambda item: item.x0))


@dataclass
class StatementEntry:
    transaction_date: date | None
    description: str
    document_number: str | None
    movement: Decimal | None
    balance: Decimal | None
    page: int
    source_text: str
    credit: Decimal | None = None
    debit: Decimal | None = None
    extra_fields: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    @property
    def needs_review(self) -> bool:
        return bool(self.warnings) or self.transaction_date is None or self.movement is None


@dataclass
class ParseResult:
    source: Path
    entries: list[StatementEntry] = field(default_factory=list)
    rejected_lines: list[tuple[int, str, str]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    detected_extra_fields: list[str] = field(default_factory=list)
