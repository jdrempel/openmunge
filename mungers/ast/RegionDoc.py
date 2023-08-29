class RegionDoc:
    def __init__(self):
        self.instances = []

    def __repr__(self):
        return 'RegionDoc[{}]'.format(len(self.instances))

    @staticmethod
    def build(tok):
        config = RegionDoc()
        config.instances = tok.as_list()
        return config
