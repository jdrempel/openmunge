from mungers.ast.Barrier import Barrier


class BarrierDoc:
    def __init__(self, name=None):
        self._id = None
        self.name = name
        self.instances = []

    @property
    def id(self):
        return None

    @staticmethod
    def build(tok):
        config = BarrierDoc()
        config.instances = tok.as_list()
        return config

    def __repr__(self):
        return 'BarrierDoc[{}]'.format(len(self.instances))

    def to_binary(self):
        binary = bytearray()
        content_size = 0
        for instance in self.instances:
            if not isinstance(instance, Barrier):
                continue
            inst_size, inst_binary = instance.to_binary()
            content_size += inst_size
            binary.extend(inst_binary)
        return content_size, binary
