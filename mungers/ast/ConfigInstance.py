from abc import ABC


class ConfigInstance(ABC):
    def __init__(self, name, args):
        self.name = name
        self.args = args
        self.body = None

    @staticmethod
    def _build_impl(tok, force_body=False):
        tok = tok[0]
        try:
            args = tok.args.as_list()
        except AttributeError as ae:
            args = tok.args or []
        inst = ConfigInstance(tok.name, args)
        if tok.body:
            inst.body = tok.body.as_list()
        elif force_body:
            inst.body = []
        return inst

    @staticmethod
    def build_instance(tok):
        return ConfigInstance._build_impl(tok, force_body=True)

    @staticmethod
    def build_property(tok):
        return ConfigInstance._build_impl(tok, force_body=False)

    def __repr__(self):
        rv = '{name}({args})'.format(name=self.name, args=', '.join(list(map(str, self.args))))
        if self.body is not None:
            rv += '[{}]'.format(len(self.body))
        return rv

    def __str__(self):
        return repr(self)
