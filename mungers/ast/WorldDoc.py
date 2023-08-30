import pathlib

from core.util.hashing import magic
from mungers.ast.Object import Object
from mungers.chunks.Chunk import Chunk


class WorldDoc(Chunk):
    def __init__(self):
        super().__init__('wrld')
        self.light_name = None
        self.terrain_name = None
        self.sky_name = None
        self.path_name = None

        self.regions = []
        self.instances = []
        self.hints = []
        self.barriers = []

    def __repr__(self):
        return 'WorldDoc[{}]'.format(len(self.instances))

    @property
    def id(self):
        return 'wrld'

    def get_light_name(self):
        return self.light_name or ''

    def get_terrain_name(self):
        return self.terrain_name or ''

    def get_sky_name(self):
        return self.sky_name or ''

    def get_path_name(self):
        return self.path_name or ''

    @staticmethod
    def build(tok):
        world = WorldDoc()
        world.instances = tok.as_list()

        def stem_of(name: str):
            return pathlib.Path(str(name)).stem

        for instance in world.instances:
            if instance.name == magic('LightName'):
                world.light_name = stem_of(instance.args[0])
            elif instance.name == magic('TerrainName'):
                world.terrain_name = stem_of(instance.args[0])
            elif instance.name == magic('SkyName'):
                world.sky_name = stem_of(instance.args[0])
            elif instance.name == magic('PathName'):
                world.path_name = stem_of(instance.args[0])
        world.instances = [x for x in world.instances if isinstance(x, Object)]
        return world
