from mungers.MungerBase import MungerBase


class OdfMunge(MungerBase):
    def __init__(self):
        super().__init__('OdfMunge')

    def run(self):
        self.logger.info('Sweet')
