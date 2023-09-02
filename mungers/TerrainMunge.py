from mungers.MungerBase import MungerBase
from mungers.chunks.Chunk import Chunk
from mungers.util.TerrainReader import TerrainReader


class TerrainMunge(MungerBase):
    def __init__(self):
        super().__init__('TerrainMunge')

    def run(self):
        extension = '.terrain'

        if not self.args.output_dir.exists():
            self.args.output_dir.mkdir(parents=True)

        input_files = self.get_input_files()

        if not input_files:
            self.logger.info('No input files were found. Stopping...')
            return

        for input_file in input_files:
            terrain_reader = TerrainReader(input_file)
            terrain_data = terrain_reader.read()
            with Chunk('ucfb').open() as root:
                with terrain_data.open(root):
                    pass
