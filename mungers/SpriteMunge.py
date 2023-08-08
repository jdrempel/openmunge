from mungers.MungerBase import MungerBase


class SpriteMunge(MungerBase):
    def __init__(self):
        super().__init__('SpriteMunge')

    def run(self):
        self.logger.info('Sweet')
