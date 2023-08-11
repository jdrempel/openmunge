import struct
from core.util.hashing import fnv1a_hash


class Config:
    def __init__(self, name=None):
        self._id = None
        self.name = name
        self.version = 10
        self.properties = []
        self.instances = []

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if not isinstance(value, str):
            raise TypeError('Config id must be type str.')
        if len(value) > 4:
            raise ValueError('Config id must be no longer than 4 bytes.')
        while len(value) < 4:
            value += '_'
        self._id = value

    @staticmethod
    def build(tok):
        config = Config()
        config.instances = tok.as_list()
        return config

    def __repr__(self):
        return 'Config[{}]'.format(len(self.instances))

    def to_binary(self):
        binary = bytearray()
        binary.extend(bytes(self.id, encoding='ascii'))
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
