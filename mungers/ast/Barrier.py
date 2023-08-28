import struct

from core.util.hashing import fnv1a_hash_str as magic
from core.types.math import Vector3, Matrix33
from mungers.chunks.Chunk import Chunk
from mungers.serializers.BinarySerializer import BinarySerializer


class Barrier(Chunk):
    CHILD_BLACKLIST = {magic(x) for x in ('Position', 'Rotation')}

    def __init__(self):
        super().__init__('BARR')
        self.name = None
        self.args = []
        self.body = None
        self.barrier_name = None
        self.flags = None
        self.corners: list[Vector3] = []
        self.rotation = Matrix33()
        self.position = Vector3()
        self.size = Vector3()
        self.y_axis = Vector3()
        self.side_0 = Vector3()
        self.side_1 = Vector3()

    def __str__(self):
        return 'Barrier({})'.format(self.barrier_name)

    @staticmethod
    def build(tok):
        inst = Barrier()
        inst.name = tok[0].name
        inst.barrier_name = tok[0].args[0]
        inst.barrier_name.value = inst.barrier_name.value.lower()
        body = tok[0].body.as_list() or []
        for x in body:
            if x.name == magic('Corner'):
                coords = [float(arg) for arg in x.args]
                coords[1] = 0.0
                inst.corners.append(Vector3(*coords))
            elif x.name == magic('Flag'):
                inst.flags = int(x.args[0])
        inst.setup_corners()
        return inst

    def setup_corners(self):
        # Determine size and rotation from the corners
        # Size is from midpoints to edges
        self.side_0 = self.corners[0] - self.corners[1]
        self.side_1 = self.corners[1] - self.corners[2]
        self.y_axis = self.side_0.cross(self.side_1)
        if self.y_axis.y > 0.0:
            self.corners = [self.corners[i] for i in (0, 3, 2, 1)]
        self.size = Vector3((self.corners[0]-self.corners[1]).magnitude(),
                            0.0,
                            (self.corners[1]-self.corners[2]).magnitude()) / 2.0

        self.position = (self.corners[0] + self.corners[2]) / 2.0

    def get_transform(self):
        x_axis = self.side_0.normalized()
        x_axis.z *= -1.0
        z_axis = self.side_1.normalized()
        z_axis.z *= -1.0
        self.rotation = Matrix33(vectors=(z_axis, Vector3(0.0, 1.0, 0.0), x_axis))

        xfrm_rot = self.rotation.flatten()
        xfrm_pos = self.position.flatten()
        xfrm = xfrm_rot + xfrm_pos
        return xfrm

    def get_size(self):
        return self.size.flatten()

    def to_binary(self):
        ser = BinarySerializer
        fmt_str = '<4sI'  # DATAsize

        # INFOsize: {NAMEsizeStr..., XFRMsizeRot[9]Pos[3], SIZEsizeSz[3], FLAGsizeFlag}
        info_fmt_str = '<4sI4sI{nsize}s4sI12f4sI3f4sII'

        name = self.barrier_name.to_binary_no_annotation(strict=True)
        nsize = ser.get_padded_len(len(name))

        # Determine size and rotation from the corners
        # Size is from midpoints to edges
        side_0 = self.corners[0] - self.corners[1]
        side_1 = self.corners[1] - self.corners[2]
        y_axis = side_0.cross(side_1)

        if y_axis.y > 0.0:
            self.corners = [self.corners[i] for i in (0, 3, 2, 1)]
        self.size = Vector3((self.corners[0]-self.corners[1]).magnitude(),
                            0.0,
                            (self.corners[1]-self.corners[2]).magnitude()) / 2.0

        self.position = (self.corners[0] + self.corners[2]) / 2.0

        x_axis = side_0.normalized()
        x_axis.z *= -1.0
        z_axis = side_1.normalized()
        z_axis.z *= -1.0
        self.rotation = Matrix33(vectors=(z_axis, Vector3(0.0, 1.0, 0.0), x_axis))

        xfrm_rot = self.rotation.flatten()
        xfrm_pos = self.position.flatten()
        xfrm = xfrm_rot + xfrm_pos

        info_fmt_str = info_fmt_str.format(nsize=nsize)
        info_size = 4 * 3 + 4 + nsize + 4 + 4 * len(xfrm)
        info_bytes = struct.pack(info_fmt_str,
                                 b'INFO', info_size,
                                 b'NAME', len(name), name,
                                 b'XFRM', 48, *xfrm,
                                 b'SIZE', 12, *self.size.flatten(),
                                 b'FLAG', 4, self.flags)
        total_info_size = len(info_bytes)
        fmt_str += '{}s'.format(total_info_size)

        header = b'BARR'
        size = len(info_bytes)
        binary = struct.pack(fmt_str, header, size, info_bytes)
        total_size = ser.get_padded_len(size + 8)
        return total_size, binary
