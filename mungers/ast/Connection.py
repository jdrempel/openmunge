from core.util.hashing import magic
from mungers.chunks.Chunk import Chunk

CONNECTION_NAME_SIZE = 16


class Connection:
    def __init__(self):
        self.name = None
        self.connection_name = None
        self.start_hub = None
        self.end_hub = None
        self.endpoints = []
        self.flag = 0
        self.one_way = False
        self.jump = False
        self.jet_jump = False
        self.dynamic_group = None

    def __str__(self):
        return 'Connection({})'.format(self.connection_name)

    @staticmethod
    def build(tok):
        inst = Connection()
        inst.name = tok[0].name
        inst.connection_name = tok[0].args[0]
        body = tok[0].body.as_list() or []
        for x in body:
            if x.name == magic('Start'):
                inst.start_hub = str(x.args[0])
            elif x.name == magic('End'):
                inst.end_hub = str(x.args[0])
            elif x.name == magic('Flag'):
                inst.flag = int(x.args[0])
            elif x.name == magic('OneWay'):
                inst.one_way = True
            elif x.name == magic('JetJump'):
                inst.jet_jump = True
            elif x.name == magic('Jump'):
                inst.jump = True
            elif x.name == magic('Dynamic'):
                inst.dynamic_group = int(x.args[0])
        return inst

    def to_binary(self, parent: Chunk, plan_doc):
        parent.write_str_fixed(self.connection_name, CONNECTION_NAME_SIZE)
        parent.write_byte(self.endpoints[0])
        parent.write_byte(self.endpoints[1])
        parent.write_int(self.flag)
        parent.write_int(int(self.one_way) | (int(self.jump) << 1) | (int(self.jet_jump) << 2))

    def has_type(self, t: int) -> bool:
        return bool(self.flag & (2**t))

    def has_type_or_lower(self, t: int) -> bool:
        shifted_type = 2**t
        while True:
            if shifted_type == 0:
                return False
            if self.flag & shifted_type:
                return True
            shifted_type >>= 1

    def has_type_or_higher(self, t: int) -> bool:
        shifted_type = 2**t
        while True:
            if shifted_type >= 32:
                return False
            if self.flag & shifted_type:
                return True
            shifted_type <<= 1

    def get_hub_opposite_name(self, hub):
        if self.start_hub == hub.hub_name:
            return self.end_hub
        elif self.end_hub == hub.hub_name:
            return self.start_hub
        return None
