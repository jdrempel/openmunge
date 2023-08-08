from mungers.MungerBase import MungerBase


class TextMunge(MungerBase):
    def __init__(self):
        super().__init__('TextMunge')

    def run(self):
        self.logger.info('Sweet')
