from core.util.hashing import magic
from core.util.math_util import mangle_quat, quat_to_rotation_matrix
from mungers.chunks.Chunk import Chunk


class Region(Chunk):
    CHILD_BLACKLIST = {magic(x) for x in ('Position', 'Rotation', 'Size')}
    TYPE_MAP = ['box', 'sphere', 'cylinder']

    def __init__(self):
        super().__init__('regn')
        self.body = []
        self.class_info = None
        self.region_type = None
        self.rotation = [0.0] * 4
        self.position = [0.0] * 3
        self.size = [0.0] * 3

    def __str__(self):
        return 'Region({cls})'.format(cls=self.class_info)

    @staticmethod
    def build(tok):
        inst = Region()
        inst.name = tok[0].name
        inst.class_info = str(tok[0].args[0])
        inst.region_type = Region.TYPE_MAP[int(tok[0].args[1])]
        body = tok[0].body.as_list() or []
        for x in body:
            if x.name == magic('Rotation'):
                inst.rotation = [float(arg) for arg in x.args]
            elif x.name == magic('Position'):
                inst.position = [float(arg) for arg in x.args]
            elif x.name == magic('Size'):
                inst.size = [float(arg) for arg in x.args]
        inst.body = [item for item in body if item.name not in Region.CHILD_BLACKLIST]
        return inst

    def get_transform(self):
        xfrm_rot_mat = quat_to_rotation_matrix(mangle_quat(self.rotation))  # Thanks Pandemic
        xfrm_rot = [i for row in xfrm_rot_mat for i in row]

        xfrm_pos = [float(v) for v in self.position]
        xfrm_pos[2] = -xfrm_pos[2]  # Thanks Pandemic

        xfrm = xfrm_rot + xfrm_pos
        return xfrm
