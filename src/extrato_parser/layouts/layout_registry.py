from .caixa import CaixaStatementLayout
from .generic import GenericStatementLayout
from .inter import InterStatementLayout
from .itau import ItauStatementLayout
from .santander import SantanderStatementLayout
from .statement_layout import StatementLayout


class LayoutRegistry:
    def registered(self) -> list[StatementLayout]:
        return [
            InterStatementLayout(),
            CaixaStatementLayout(),
            ItauStatementLayout(),
            SantanderStatementLayout(),
            GenericStatementLayout(),
        ]
