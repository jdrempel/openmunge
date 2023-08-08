from abc import ABC

from mungers.ast.AstNode import AstNode


class Config(AstNode, ABC):
    def __init__(self, name):
        super().__init__(name)
        self.version = 10
        self.properties = []
        self.instances = []
