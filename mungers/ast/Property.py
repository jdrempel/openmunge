class Property:
    def __init__(self):
        self.name = None
        self.args = []
        self.body = None

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, str(self.name))

    @staticmethod
    def build(tok):
        inst = Property()
        inst.name = tok.name
        inst.args = tok.args or []
        inst.body = tok.body or None
        return inst
