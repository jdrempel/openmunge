from mungers.MungerBase import MungerBase


class LocalizeMunge(MungerBase):
    def __init__(self):
        super().__init__('LocalizeMunge')

    def run(self):
        self.logger.info('Sweet')
