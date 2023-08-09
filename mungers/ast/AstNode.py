from abc import ABC
from typing import Protocol


class VisitorProtocol(Protocol):
    def visit_enter(self, node):
        ...

    def visit_leave(self, node):
        ...


class AstNode(ABC):
    def accept(self, visitor: VisitorProtocol):
        return visitor.visit_enter(self)
