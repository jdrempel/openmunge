import pathlib
import struct

from core.util.hashing import fnv1a_hash
from mungers.ast.Object import Object
from mungers.serializers.BinarySerializer import BinarySerializer


class WorldDoc:
    SPECIAL_NAMES = {'TerrainName', 'SkyName'}

    def __init__(self, name=None):
        self._id = None
        self.name = name
        self.version = 3
        self.instances = []
        self.terrain_name = None
        self.sky_name = None

    def __repr__(self):
        return 'WorldDoc[{}]'.format(len(self.instances))

    @property
    def id(self):
        return 'wrld'

    @staticmethod
    def build(tok):
        world = WorldDoc()
        world.instances = tok.as_list()
        return world

    def to_binary(self, region_data=None, hint_binary=None, barrier_binary=None):
        binary = bytearray()
        binary.extend(bytes(self.id, encoding='ascii'))

        content_size = 0
        instance_binaries = bytearray()
        terrain_binary = bytearray()
        sky_binary = bytearray()
        ser = BinarySerializer
        for instance in self.instances:
            if str(instance.name) == 'TerrainName':
                arg = pathlib.Path(str(instance.args[0])).stem
                terrain_name = bytes(arg, encoding='ascii') + b'\x00'
                terrain_name_size = ser.get_padded_len(len(terrain_name))
                terrain_binary = struct.pack('<4sI{}s'.format(terrain_name_size), b'TNAM', len(terrain_name),
                                             terrain_name)
                continue
            elif str(instance.name) == 'SkyName':
                arg = pathlib.Path(str(instance.args[0])).stem
                sky_name = bytes(arg, encoding='ascii') + b'\x00'
                sky_name_size = ser.get_padded_len(len(sky_name))
                sky_binary = struct.pack('<4sI{}s'.format(sky_name_size), b'SNAM', len(sky_name), sky_name)
                continue
            inst_size, inst_binary = instance.to_binary()
            content_size += inst_size
            instance_binaries.extend(inst_binary)

        name = bytes(str(self.name).lower(), encoding='ascii') + b'\x00'
        name_size = ser.get_padded_len(len(name))
        name_binary = b'NAME' + struct.pack('<I4s', name_size, name) + terrain_binary + sky_binary

        region_count, region_binary = region_data
        object_count = sum([1 for x in self.instances if isinstance(x, Object)])
        info_binary = b'INFO' + struct.pack('<III', 2*4, region_count, object_count)

        content_binary = name_binary + info_binary
        if region_binary is not None:
            content_binary += region_binary[1]
        content_binary += instance_binaries
        if hint_binary is not None:
            content_binary += hint_binary[1]
        if barrier_binary is not None:
            content_binary += barrier_binary[1]
        size = len(content_binary)
        binary.extend(struct.pack('<I', size))
        binary.extend(content_binary)
        return content_size, binary
