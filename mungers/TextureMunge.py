from mungers.MungerBase import MungerBase


class TextureMunge(MungerBase):
    def __init__(self):
        super().__init__('TextureMunge')

    def run(self):
        self.logger.info('Sweet')
