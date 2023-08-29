class ReqList:
    def __init__(self, header, entries):
        self.header = header
        self.entries = entries or []

    def __str__(self):
        return 'ReqList({header})[{n}]'.format(header=self.header, n=len(self.entries))

    def __repr__(self):
        return str(self)

    @staticmethod
    def build(tok):
        entries = tok.entries
        if entries:
            entries = tok.entries.as_list()
        inst = ReqList(tok.header, entries)
        return inst
