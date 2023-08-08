from mungers.MungerBase import MungerBase


class BinMunge(MungerBase):
    def __init__(self):
        super().__init__('BinMunge')

    def run(self):
        self.logger.info('Sweet')
