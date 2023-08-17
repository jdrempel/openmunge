import struct

from core.util.hashing import fnv1a_hash
from mungers.ast.Object import Object


class World:
    def __init__(self, name=None):
        self._id = None
        self.name = name
        self.version = 3
        self.instances = []

    def __repr__(self):
        return 'World[{}]'.format(len(self.instances))

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if not isinstance(value, str):
            raise TypeError('World id must be type str.')
        if len(value) > 4:
            raise ValueError('World id must be no longer than 4 bytes.')
        while len(value) < 4:
            value += '_'
        self._id = value

    @staticmethod
    def build(tok):
        world = World()
        world.instances = tok.as_list()
        return world

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

        region_count = sum([1 for x in self.instances if x.__class__.__name__ == 'Region'])
        object_count = sum([1 for x in self.instances if isinstance(x, Object)])
        info_binary = b'INFO' + struct.pack('<III', 2*4, region_count, object_count)

        content_binary = name_binary + info_binary + instance_binaries
        size = len(content_binary)
        binary.extend(struct.pack('<I', size))
        binary.extend(content_binary)
        return content_size, binary
