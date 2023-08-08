from mungers.MungerBase import MungerBase


class TerrainMunge(MungerBase):
    def __init__(self):
        super().__init__('TerrainMunge')

    def run(self):
        self.logger.info('Sweet')
