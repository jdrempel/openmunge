from mungers.ast.Property import Property


class Object(Property):
    CHILD_BLACKLIST = {'SeqNo', 'NetworkId'}

    @staticmethod
    def build(tok):
        inst = Object()
        inst.name = tok[0]
        return inst

    def __call__(self, owner):
        args = owner.args[:2]  # Cut out the sequence number
        body = [item for item in owner.body if str(item.name) not in Object.CHILD_BLACKLIST]
        return args, body
