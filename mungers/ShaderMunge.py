from mungers.MungerBase import MungerBase


class ShaderMunge(MungerBase):
    def __init__(self):
        super().__init__('ShaderMunge')

    def run(self):
        self.logger.info('Sweet')
