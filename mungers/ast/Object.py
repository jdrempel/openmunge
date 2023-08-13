from mungers.ast.Property import Property


class Object(Property):
    CHILD_BLACKLIST = {'SeqNo', 'NetworkId'}

    @staticmethod
    def build(tok):
        inst = Object()
        inst.name = tok[0].name
        inst.label = tok[0].args[0]
        inst.class_ = tok[0].args[1]
        body = tok[0].body.as_list() or []
        inst.body = [item for item in body if str(item.name) not in Object.CHILD_BLACKLIST]
        return inst
