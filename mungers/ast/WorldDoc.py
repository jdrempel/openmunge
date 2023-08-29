import pathlib
import struct
from contextlib import contextmanager

from mungers.ast.Object import Object
from mungers.chunks.Chunk import Chunk
from mungers.serializers.BinarySerializer import BinarySerializer


class WorldDoc(Chunk):
    SPECIAL_NAMES = {'TerrainName', 'SkyName'}

    def __init__(self):
        super().__init__('wrld')
        self.terrain_name = None
        self.sky_name = None
        self.regions = []
        self.instances = []
        self.hints = []
        self.barriers = []

    def __repr__(self):
        return 'WorldDoc[{}]'.format(len(self.instances))

    @property
    def id(self):
        return 'wrld'

    @staticmethod
    def build(tok):
        world = WorldDoc()
        world.instances = tok.as_list()
        for instance in world.instances:
            if str(instance.name) == 'TerrainName':
                world.terrain_name = pathlib.Path(str(instance.args[0])).stem
            elif str(instance.name) == 'SkyName':
                world.sky_name = pathlib.Path(str(instance.args[0])).stem
        world.instances = [x for x in world.instances if isinstance(x, Object)]
        return world
