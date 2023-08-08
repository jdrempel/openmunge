from mungers.ast.AstNode import AstNode


class AstRoot(AstNode):
    def __init__(self):
        super().__init__('ucfb')
