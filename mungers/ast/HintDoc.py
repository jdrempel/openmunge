class HintDoc:
    def __init__(self):
        self.instances = []

    def __repr__(self):
        return 'HintDoc[{}]'.format(len(self.instances))

    @staticmethod
    def build(tok):
        config = HintDoc()
        config.instances = tok.as_list()
        return config
