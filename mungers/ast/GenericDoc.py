class GenericDoc:
    def __init__(self):
        self.instances = []

    @staticmethod
    def build(tok):
        doc = GenericDoc()
        doc.instances = tok.as_list()
        return doc
