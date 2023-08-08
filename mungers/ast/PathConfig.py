from mungers.ast.Config import Config


class PathConfig(Config):
    def __init__(self):
        super().__init__('path')

    @staticmethod
    def build(tok):
        config = PathConfig()
        config.instances = tok.as_list()
        return config

    def __repr__(self):
        return 'PathConfig[{}]'.format(len(self.instances))
