import pathlib
from collections import defaultdict
from dataclasses import dataclass
from enum import IntEnum

from core.types.math import Vector4
from core.util.math_util import unpack_srgb_bgra
from mungers.chunks.Chunk import Chunk
from mungers.util.BinaryReader import BinaryReader

CLUSTER_SIZE = 4
FOLIAGE_PATCH_SIZE = 2
NUM_TEXTURES = 16
NUM_WATER_LAYERS = 16
TERRAIN_STR_SIZE = 32

CLUSTER_INFO_WATER = 0x10000

SZ_UINT8 = 1
SZ_UINT16 = 2
SZ_UINT32 = 4
SZ_FLOAT = 4


class TerrainVersion(IntEnum):
    SWBF1 = 21
    SWBF2 = 22


class TerrainActiveFlags:
    def __init__(self, value: int = 0):
        self.terrain = bool(value & (1 << 0))
        self.water = bool(value & (1 << 1))
        self.foliage = bool(value & (1 << 2))
        self.extra_lightmap = bool(value & (1 << 3))


@dataclass
class TerrainHeader:
    magic_number: bytes
    version: int
    active_left_offset: int
    active_top_offset: int
    active_right_offset: int
    active_bottom_offset: int
    ex_header_size: int
    texture_scales: list
    texture_axes: list
    texture_rotations: list
    height_scale: float
    grid_scale: float
    pre_lit: bool
    terrain_length: int
    foliage_patch_size: int


@dataclass
class WaterSettings:
    height: float
    unused: list
    u_vel: float
    v_vel: float
    u_rep: float
    v_rep: float
    colour: Vector4
    texture: str


class Terrain(Chunk):
    def __init__(self, header: TerrainHeader):
        super().__init__('tern')
        self.version = header.version
        self.length = header.active_right_offset - header.active_left_offset
        self.height_scale = header.height_scale
        self.grid_scale = header.grid_scale
        self.texture_scales = header.texture_scales
        self.texture_axes = header.texture_axes

        self.active_flags = TerrainActiveFlags()
        self.texture_names = []
        self.detail_texture_name = None

        self.water_settings = None
        self.water_map = defaultdict(dict)

        self.height_map = defaultdict(dict)
        self.colour_map = defaultdict(dict)
        self.light_map = defaultdict(dict)
        self.light_map_extra = defaultdict(dict)
        self.texture_weight_maps = defaultdict(lambda: defaultdict(dict))

    def set_water_settings(self, settings):
        self.water_settings = settings


class TerrainReader(BinaryReader):
    def read(self) -> Terrain:
        # Credit to sleepy/PrismaticFlower for the understanding of the inner workings here

        header = self.read_header()
        terrain = Terrain(header)

        extra_lightmap = False

        if header.version == TerrainVersion.SWBF2:
            active_flags_byte = self.read_u8()
            terrain.active_flags = TerrainActiveFlags(active_flags_byte)
            extra_lightmap = terrain.active_flags.extra_lightmap

        for i in range(NUM_TEXTURES):
            terrain.texture_names.append(self.read_terr_str())
            detail_name = self.read_terr_str()
            if i == 0:
                terrain.detail_texture_name = detail_name

        water_settings = self.read_water_settings()
        terrain.set_water_settings(water_settings)

        # Decals (unused)
        for _ in range(NUM_TEXTURES):
            self.skip(TERRAIN_STR_SIZE)
        decal_tile_count = self.read_u32()
        for i in range(decal_tile_count):
            self.skip(SZ_UINT32*3)  # 3x u32
            self.skip(SZ_FLOAT*2*4)  # 4x vecf2

        self.read_unused_foliage_section()

        active_offset = header.terrain_length - terrain.length // 2
        active_end = active_offset + abs(terrain.length)

        def read_map(data_read_method, data_size):
            output = defaultdict(dict)
            for y_ in range(header.terrain_length-1, -1, -1):
                self.skip(active_offset*data_size)
                if active_offset <= y_ < active_end:
                    for x_ in range(terrain.length):
                        output[x_][y_ - active_offset] = data_read_method()
                else:
                    self.skip(terrain.length*data_size)
                self.skip(active_offset*data_size)
            return output

        def read_texture_weight_map():
            output = defaultdict(lambda: defaultdict(dict))
            for y_ in range(header.terrain_length - 1, -1, -1):
                self.skip(active_offset*NUM_TEXTURES)
                if active_offset <= y_ < active_end:
                    for x_ in range(terrain.length):
                        for t_ in range(NUM_TEXTURES):
                            output[x_][y_ - active_offset][t_] = self.read_u8()
                else:
                    self.skip(terrain.length*NUM_TEXTURES)
                self.skip(active_offset*NUM_TEXTURES)
            return output

        texture_weight_map = defaultdict(lambda: defaultdict(dict))

        try:
            terrain.height_map = read_map(self.read_u16, SZ_UINT16)
            terrain.colour_map = read_map(self.read_u32, SZ_UINT32)
            terrain.light_map = read_map(self.read_u32, SZ_UINT32)
            if extra_lightmap:
                terrain.light_map_extra = read_map(self.read_u32, SZ_UINT32)
            texture_weight_map = read_texture_weight_map()
        except IOError:
            # Some stock .ter files end without all data present
            pass  # TODO log something probably

        for y in range(terrain.length):
            for x in range(terrain.length):
                for i in range(NUM_TEXTURES):
                    terrain.texture_weight_maps[i][x][y] = texture_weight_map[x][y][i]

        loaded_cluster_length = terrain.length // CLUSTER_SIZE
        cluster_length = header.terrain_length // CLUSTER_SIZE
        cluster_count = cluster_length ** 2
        cluster_active_offset = active_offset // CLUSTER_SIZE
        cluster_active_end = active_end // CLUSTER_SIZE

        self.skip(cluster_count * SZ_UINT16)
        self.skip(cluster_count * SZ_UINT16)

        for y in range(cluster_length-1, -1, -1):
            self.skip(cluster_active_offset*SZ_UINT32)
            if cluster_active_offset <= y < cluster_active_end:
                for x in range(loaded_cluster_length):
                    cluster_flags = self.read_u32()
                    terrain.water_map[x][y-cluster_active_offset] = bool(cluster_flags & CLUSTER_INFO_WATER)
            else:
                self.skip(loaded_cluster_length*SZ_UINT32)
            self.skip(cluster_active_offset*SZ_UINT32)

        return terrain

    def read_terr_str(self):
        return self.read_str_fixed(TERRAIN_STR_SIZE)

    def read_header(self):
        header = TerrainHeader(
            magic_number=self.read_bytes(4),
            version=self.read_u32(),
            active_left_offset=self.read_u16(),
            active_top_offset=self.read_u16(),
            active_right_offset=self.read_u16(),
            active_bottom_offset=self.read_u16(),
            ex_header_size=self.read_u32(),
            texture_scales=[self.read_f32() for _ in range(NUM_TEXTURES)],
            texture_axes=[self.read_u8() for _ in range(NUM_TEXTURES)],
            texture_rotations=[self.read_f32() for _ in range(NUM_TEXTURES)],
            height_scale=self.read_f32(),
            grid_scale=self.read_f32(),
            pre_lit=bool(self.read_u32()),
            terrain_length=self.read_u32(),
            foliage_patch_size=self.read_u32(),
        )
        if header.magic_number != b'TERR':
            raise ValueError('Magic number != TERR, file {} may be corrupt.'.format(self._stream.name))
        if header.terrain_length > 1024:
            raise ValueError('Terrain length is too long. Max is 1024.')
        if header.foliage_patch_size != FOLIAGE_PATCH_SIZE:
            raise ValueError('Foliage patch size != 2.')
        return header

    def read_water_settings(self):
        water_settings = []
        for _ in range(NUM_WATER_LAYERS):
            water_settings.append(WaterSettings(
                height=self.read_f32(),
                unused=[self.read_f32() for _ in range(3)],
                u_vel=self.read_f32(),
                v_vel=self.read_f32(),
                u_rep=self.read_f32(),
                v_rep=self.read_f32(),
                colour=unpack_srgb_bgra(self.read_u32()),
                texture=self.read_terr_str(),
            ))
        return water_settings[1]

    def read_unused_foliage_section(self):
        foliage_cluster_count = self.read_u32()
        for i in range(foliage_cluster_count):
            self.skip(4*6)  # 6x u32
        foliage_model_count = self.read_u32()
        for i in range(foliage_model_count):
            self.skip(4*7)  # 7x u32


if __name__ == '__main__':
    path = pathlib.Path('/home/jeremy/projects/data_ABC/Worlds/ABC/world1/ABC.TER')
    with TerrainReader(path) as reader:
        reader.read()
