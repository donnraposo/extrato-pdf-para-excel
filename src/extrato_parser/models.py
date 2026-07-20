"""Fachada de compatibilidade para imports anteriores à Clean Architecture."""

from .domain.entities import ParseResult, PhysicalLine, StatementEntry, Word

__all__ = ["ParseResult", "PhysicalLine", "StatementEntry", "Word"]
