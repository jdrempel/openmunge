class Property:
    def __init__(self):
        self.name = None

    def __call__(self, owner):
        return owner.args, owner.body

    def __str__(self):
        return str(self.name)

    @staticmethod
    def build(tok):
        inst = Property()
        inst.name = tok[0]
        return inst
