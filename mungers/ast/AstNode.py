from abc import ABC


class AstNode(ABC):
    def __init__(self, name=None):
        self.name = name
        self.size = 0
