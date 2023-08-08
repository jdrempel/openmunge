from abc import ABC, abstractmethod


class AstVisitor(ABC):
    @abstractmethod
    def traverse(self, node):
        ...

    @abstractmethod
    def visit_enter(self, node):
        ...

    @abstractmethod
    def visit_leave(self, node):
        ...
