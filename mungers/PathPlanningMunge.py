from mungers.MungerBase import MungerBase


class PathPlanningMunge(MungerBase):
    def __init__(self):
        super().__init__('PathPlanningMunge')

    def run(self):
        self.logger.info('Sweet')
