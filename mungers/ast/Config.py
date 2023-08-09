from abc import ABC

from mungers.ast.AstNode import AstNode


class Config(AstNode, ABC):
    def __init__(self, name, label=None):
        self.label = label
        self.name = name
        self.version = 10
        self.properties = []
        self.instances = []
