from .statement_layout import StatementLayout
from ..domain.entities import PhysicalLine


class LayoutDetector:
    def __init__(self, layouts: list[StatementLayout]) -> None:
        self._layouts = layouts

    def detect(self, lines: list[PhysicalLine]) -> StatementLayout:
        for layout in self._layouts:
            if layout.matches(lines):
                return layout
        return self._layouts[-1]
