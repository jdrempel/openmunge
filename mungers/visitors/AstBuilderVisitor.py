from mungers.visitors.AstVisitor import AstVisitor


class AstBuilderVisitor(AstVisitor):
    """Note: Doesn't visit AstNodes, builds them by visiting parse data."""
    def traverse(self, node):
        ...

    def visit_enter(self, node):
        ...

    def visit_leave(self, node):
        ...
    ...
