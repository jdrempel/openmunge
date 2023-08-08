from mungers.MungerBase import MungerBase


class PathMunge(MungerBase):
    def __init__(self):
        super().__init__('PathMunge')

    def run(self):
        self.logger.info('Sweet')
