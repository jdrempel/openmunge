from abc import ABC, abstractmethod
from typing import Protocol


class NodeProtocol(Protocol):
    def accept(self, visitor):
        ...

    def get_size(self):
        ...


class AstVisitor(ABC):
    @abstractmethod
    def visit_enter(self, node: NodeProtocol):
        ...

    @abstractmethod
    def visit_leave(self, node: NodeProtocol):
        ...
