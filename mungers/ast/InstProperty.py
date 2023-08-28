from core.util.hashing import fnv1a_hash_str
from mungers.chunks.Chunk import Chunk


class InstProperty(Chunk):
    def __init__(self, name, args):
        super().__init__('PROP')
        self.name = fnv1a_hash_str(name)
        self.args = args
        self.body = None

    @staticmethod
    def build(tok):
        tok = tok[0]
        try:
            args = tok.args.as_list()
        except AttributeError:
            args = tok.args or []
        inst = InstProperty(tok.name, args)
        return inst
