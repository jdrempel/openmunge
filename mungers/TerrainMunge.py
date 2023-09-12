from mungers.MungerBase import MungerBase
from mungers.chunks.Chunk import Chunk
from mungers.util.TerrainReader import TerrainReader


class TerrainMunge(MungerBase):
    def __init__(self):
        super().__init__('TerrainMunge')

    def run(self):
        extension = '.terrain'

        for input_file in self.input_files:
            terrain_reader = TerrainReader(input_file)
            terrain_data = terrain_reader.read()
            with Chunk('ucfb').open() as root:
                with terrain_data.open(root):
                    pass
