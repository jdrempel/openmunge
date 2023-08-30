from core.util.hashing import magic
from core.util.math_util import quat_to_rotation_matrix, mangle_quat
from mungers.chunks.Chunk import Chunk


class Object(Chunk):
    CHILD_BLACKLIST = {magic(x) for x in ('SeqNo', 'NetworkId', 'ChildPosition', 'ChildRotation')}

    def __init__(self):
        super().__init__('inst')
        self.name = None
        self.args = []
        self.body = None
        self.label = None
        self.class_ = None
        self.rotation = [0.0] * 4
        self.position = [0.0] * 3

    def __str__(self):
        return 'Object({cls})'.format(cls=self.label)

    @staticmethod
    def build(tok):
        inst = Object()
        inst.name = tok[0].name
        inst.label = tok[0].args[0]
        inst.class_ = tok[0].args[1]
        body = tok[0].body.as_list() or []
        for x in body:
            if x.name == magic('ChildRotation'):
                inst.rotation = [float(arg) for arg in x.args]
            elif x.name == magic('ChildPosition'):
                inst.position = [float(arg) for arg in x.args]
        inst.body = [item for item in body if item.name not in Object.CHILD_BLACKLIST]
        return inst

    def get_transform(self):
        xfrm_rot_mat = quat_to_rotation_matrix(mangle_quat(self.rotation))  # Thanks Pandemic
        xfrm_rot = [i for row in xfrm_rot_mat for i in row]

        xfrm_pos = [float(v) for v in self.position]
        xfrm_pos[2] = -xfrm_pos[2]  # Thanks Pandemic

        xfrm = xfrm_rot + xfrm_pos
        return xfrm

    def get_class_name(self):
        return str(self.class_)
