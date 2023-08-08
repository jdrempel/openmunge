from mungers.MungerBase import MungerBase


class ShadowMunge(MungerBase):
    def __init__(self):
        super().__init__('ShadowMunge')

    def run(self):
        self.logger.info('Sweet')
