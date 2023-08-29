class BarrierDoc:
    def __init__(self):
        self.instances = []

    def __repr__(self):
        return 'BarrierDoc[{}]'.format(len(self.instances))

    @staticmethod
    def build(tok):
        config = BarrierDoc()
        config.instances = tok.as_list()
        return config
