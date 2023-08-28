import struct

from core.util.hashing import fnv1a_hash_str as magic
from core.util.math_util import quat_to_rotation_matrix, mangle_quat
from mungers.chunks.Chunk import Chunk
from mungers.serializers.BinarySerializer import BinarySerializer


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

    def to_binary(self):
        ser = BinarySerializer
        fmt_str = '<4sI'  # DATAsize

        # INFOsize: {TYPEsizeStr..., NAMEsizeStr..., XFRMsizeRot[9]Pos[3]}
        info_fmt_str = '<4sI4s{tsize}s4s{nsize}s4sI12f'

        type_ = self.class_.to_binary_no_annotation()
        tsize = ser.get_padded_len(len(type_))

        name = self.label.to_binary_no_annotation()
        nsize = ser.get_padded_len(len(name))

        xfrm_rot_mat = quat_to_rotation_matrix(mangle_quat(self.rotation))  # Thanks Pandemic
        xfrm_rot = [i for row in xfrm_rot_mat for i in row]

        xfrm_pos = [float(v) for v in self.position]
        xfrm_pos[2] = -xfrm_pos[2]  # Thanks Pandemic

        xfrm = xfrm_rot + xfrm_pos

        info_fmt_str = info_fmt_str.format(tsize=tsize, nsize=nsize)
        info_size = 4 * 3 + tsize + nsize + 4 + 48
        info_bytes = struct.pack(info_fmt_str,
                                 b'INFO', info_size,
                                 b'TYPE', type_,
                                 b'NAME', name,
                                 b'XFRM', 48, *xfrm)
        total_info_size = len(info_bytes)
        fmt_str += '{}s'.format(total_info_size)

        body_bytes = bytearray()
        body_fmt_str = ''
        body_size = 0
        for prop in self.body:
            if str(prop.args[0]) == '':
                continue
            prop_size, prop_bytes = prop.to_binary()
            body_bytes.extend(prop_bytes)
            body_size += prop_size
        body_fmt_str += '{}s'.format(body_size)
        body_bytes = struct.pack(body_fmt_str,  body_bytes)
        body_fmt_str = '{}s'.format(len(body_bytes))
        fmt_str += body_fmt_str

        header = b'inst'
        size = len(info_bytes)
        if self.body is not None:
            size += len(body_bytes)
        binary = struct.pack(fmt_str, header, size, info_bytes, body_bytes)
        total_size = ser.get_padded_len(size + 8)
        if self.body is not None and len(body_bytes):
            total_size += len(body_bytes)
        return total_size, binary
