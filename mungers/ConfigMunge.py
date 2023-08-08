from mungers.MungerBase import MungerBase


class ConfigMunge(MungerBase):
    def __init__(self):
        super().__init__('ConfigMunge')

    def run(self):
        self.logger.info('Sweet')
