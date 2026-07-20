from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any


@dataclass
class StatementEntry:
    transaction_date: date | None
    description: str
    document_number: str | None
    movement: Decimal | None
    balance: Decimal | str | None
    page: int
    source_text: str
    effective_date: date | datetime | None = None
    credit: Decimal | None = None
    debit: Decimal | None = None
    extra_fields: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    balance_only: bool = False

    @property
    def needs_review(self) -> bool:
        return bool(self.warnings) or self.transaction_date is None or (self.movement is None and not self.balance_only)
