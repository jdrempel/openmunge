from mungers.MungerBase import MungerBase


class WorldMunge(MungerBase):
    def __init__(self):
        super().__init__('WorldMunge')

    def run(self):
        self.logger.info('Sweet')
