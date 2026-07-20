from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .statement_entry import StatementEntry


@dataclass
class ParseResult:
    source: Path
    entries: list[StatementEntry] = field(default_factory=list)
    rejected_lines: list[tuple[int, str, str]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    detected_extra_fields: list[str] = field(default_factory=list)
    output_fields: list[str] = field(default_factory=list)
    field_labels: dict[str, str] = field(default_factory=dict)
