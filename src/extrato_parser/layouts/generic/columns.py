from dataclasses import dataclass


@dataclass
class Columns:
    description: float
    document: float | None
    credit: float
    debit: float
    balance: float
    header_bottom: float
    credit_label: str = "Crédito (R$)"
    debit_label: str = "Débito (R$)"
