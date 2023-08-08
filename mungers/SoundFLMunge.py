from mungers.MungerBase import MungerBase


class SoundFlMunge(MungerBase):
    def __init__(self):
        super().__init__('SoundFlMunge')

    def run(self):
        self.logger.info('Sweet')
