from mungers.MungerBase import MungerBase


class FontMunge(MungerBase):
    def __init__(self):
        super().__init__('FontMunge')

    def run(self):
        self.logger.info('Sweet')
