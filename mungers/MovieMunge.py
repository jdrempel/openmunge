from mungers.MungerBase import MungerBase


class MovieMunge(MungerBase):
    def __init__(self):
        super().__init__('MovieMunge')

    def run(self):
        self.logger.info('Sweet')
