import struct

from core.util.hashing import fnv1a_hash
from mungers.ast.Property import Property
from mungers.serializers.BinarySerializer import BinarySerializer


class InstProperty(Property):
    def __init__(self, name, args):
        super().__init__()
        self.name = name
        self.args = args

    @staticmethod
    def build(tok):
        tok = tok[0]
        try:
            args = tok.args.as_list()
        except AttributeError:
            args = tok.args or []
        inst = InstProperty(tok.name, args)
        return inst

    def to_binary(self):
        ser = BinarySerializer
        header = b'PROP'
        name = fnv1a_hash(bytes(self.name, encoding='ascii'))
        val = self.args[0].to_binary_no_annotation(strict=True)
        size = len(name) + len(val)
        data_size = ser.get_padded_len(len(val))
        binary = struct.pack('<4sI4s{}s'.format(data_size), header, size, name, val)
        return len(binary), binary
