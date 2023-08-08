from mungers.MungerBase import MungerBase


class ModelMunge(MungerBase):
    def __init__(self):
        super().__init__('ModelMunge')

    def run(self):
        self.logger.info('Sweet')
