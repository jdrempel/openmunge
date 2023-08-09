import struct

from core.util.hashing import fnv1a_hash
from mungers.ast.Config import Config


class PathConfig(Config):
    def __init__(self):
        super().__init__('<empty>', label='path')

    @staticmethod
    def build(tok):
        config = PathConfig()
        config.instances = tok.as_list()
        return config

    def __repr__(self):
        return 'PathConfig[{}]'.format(len(self.instances))

    def to_binary(self):
        binary = bytearray()
        binary.extend(b'path')
        content_size = 0
        instance_binaries = bytearray()
        for instance in self.instances:
            inst_size, inst_binary = instance.to_binary()
            content_size += inst_size
            instance_binaries.extend(inst_binary)
        name = fnv1a_hash(bytes(self.name, encoding='ascii'))
        name_binary = b'NAME' + struct.pack('<I4s', 4, name)
        content_binary = name_binary + instance_binaries
        size = len(content_binary)
        binary.extend(struct.pack('<I', size))
        binary.extend(content_binary)
        return content_size, binary
