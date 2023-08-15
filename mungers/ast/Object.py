import struct

from core.util.hashing import fnv1a_hash
from core.util.math_util import quat_to_rotation_matrix, mangle_quat
from mungers.ast.Args import StrArg
from mungers.ast.ConfigInstance import ConfigInstance
from mungers.ast.Property import Property
from mungers.serializers.BinarySerializer import BinarySerializer


class Object(Property):
    CHILD_BLACKLIST = {'SeqNo', 'NetworkId', 'ChildPosition', 'ChildRotation'}

    def __init__(self):
        super().__init__()
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
            if str(x.name) == 'ChildRotation':
                inst.rotation = [float(arg) for arg in x.args]
            elif str(x.name) == 'ChildPosition':
                inst.position = [float(arg) for arg in x.args]
        inst.body = [item for item in body if str(item.name) not in Object.CHILD_BLACKLIST]
        return inst

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

        body_bytes = bytearray()
        body_fmt_str = '<4sI'  # SCOPsize
        body_size = 0
        for inst in self.body:
            inst_size, inst_bytes = inst.to_binary()
            body_bytes.extend(inst_bytes)
            body_size += inst_size
        if body_size:
            body_fmt_str += '{}s'.format(body_size)
            body_bytes = struct.pack(body_fmt_str, b'SCOP', body_size, body_bytes)
        else:
            body_bytes = struct.pack(body_fmt_str, b'SCOP', body_size)
        body_fmt_str = '{}s'.format(len(body_bytes))
        fmt_str += body_fmt_str

        header = b'inst'
        name = fnv1a_hash(bytes(self.name, encoding='ascii'))
        size = len(name) + len(info_bytes) + 1
        if self.body is not None:
            if len(body_bytes):
                binary = struct.pack(fmt_str, header, size, name, nargs, args_bytes, body_bytes)
            else:
                binary = struct.pack(fmt_str, header, size, name, nargs, args_bytes)
        else:
            binary = struct.pack(fmt_str, header, size, name, nargs, args_bytes)
        total_size = ser.get_padded_len(size + 8)
        if self.body is not None and len(body_bytes):
            total_size += len(body_bytes)
        return total_size, binary
