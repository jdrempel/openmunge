from core.util.hashing import magic
from core.util.math_util import mangle_quat, quat_to_rotation_matrix
from mungers.chunks.Chunk import Chunk


class Hint(Chunk):
    CHILD_BLACKLIST = {magic(x) for x in ('Position', 'Rotation')}

    def __init__(self):
        super().__init__('Hint')
        self.name = None
        self.args = []
        self.body = None
        self.hint_name = None
        self.hint_type = None
        self.rotation = [0.0] * 4
        self.position = [0.0] * 3
        self.size = [0.0] * 3

    def __str__(self):
        return 'Hint({})'.format(self.hint_name)

    @staticmethod
    def build(tok):
        inst = Hint()
        inst.name = tok[0].name
        inst.hint_name = tok[0].args[0]
        inst.hint_type = tok[0].args[1]
        body = tok[0].body.as_list() or []
        for x in body:
            if x.name == magic('Rotation'):
                inst.rotation = [float(arg) for arg in x.args]
            elif x.name == magic('Position'):
                inst.position = [float(arg) for arg in x.args]
            elif x.name == magic('Size'):
                inst.size = [float(arg) for arg in x.args]
        inst.body = [item for item in body if item.name not in Hint.CHILD_BLACKLIST]
        return inst

    def get_transform(self):
        xfrm_rot_mat = quat_to_rotation_matrix(mangle_quat(self.rotation))  # Thanks Pandemic
        xfrm_rot = [i for row in xfrm_rot_mat for i in row]

        xfrm_pos = [float(v) for v in self.position]
        xfrm_pos[2] = -xfrm_pos[2]  # Thanks Pandemic

        xfrm = xfrm_rot + xfrm_pos
        return xfrm
