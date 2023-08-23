import struct

from core.util.math_util import mangle_quat, quat_to_rotation_matrix
from mungers.ast.Property import Property
from mungers.serializers.BinarySerializer import BinarySerializer


class Region(Property):
    CHILD_BLACKLIST = {'Position', 'Rotation', 'Size'}
    TYPE_MAP = [b'box\x00', b'sphere\x00', b'cylinder\x00']

    def __init__(self):
        super().__init__()
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
        inst.class_info = tok[0].args[0]
        inst.region_type = Region.TYPE_MAP[int(tok[0].args[1])]
        body = tok[0].body.as_list() or []
        for x in body:
            if str(x.name) == 'Rotation':
                inst.rotation = [float(arg) for arg in x.args]
            elif str(x.name) == 'Position':
                inst.position = [float(arg) for arg in x.args]
            elif str(x.name) == 'Size':
                inst.size = [float(arg) for arg in x.args]
        inst.body = [item for item in body if str(item.name) not in Region.CHILD_BLACKLIST]
        return inst

    def to_binary(self):
        ser = BinarySerializer
        fmt_str = '<4sI'  # DATAsize

        # INFOsize: {TYPEsizeStr..., NAMEsizeStr..., XFRMsizeRot[9]Pos[3]SIZEsizeSz[3]}
        info_fmt_str = '<4sI4sI{tsize}s4sI{nsize}s4sI12f4sI3f'

        type_ = self.region_type
        tsize = ser.get_padded_len(len(type_))

        name = self.class_info.to_binary_no_annotation(strict=True)
        nsize = ser.get_padded_len(len(name))

        xfrm_rot_mat = quat_to_rotation_matrix(mangle_quat(self.rotation))  # Thanks Pandemic
        xfrm_rot = [i for row in xfrm_rot_mat for i in row]

        xfrm_pos = [float(v) for v in self.position]
        xfrm_pos[2] = -xfrm_pos[2]  # Thanks Pandemic

        xfrm = xfrm_rot + xfrm_pos

        info_fmt_str = info_fmt_str.format(tsize=tsize, nsize=nsize)
        info_size = 4 * 3 + 4 + tsize + 4 + nsize + 4 + 4 * len(xfrm) + 4 * 2 + 4 * len(self.size)
        info_bytes = struct.pack(info_fmt_str,
                                 b'INFO', info_size,
                                 b'TYPE', tsize, type_,
                                 b'NAME', nsize, name,
                                 b'XFRM', 48, *xfrm,
                                 b'SIZE', 12, *self.size)
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

        header = b'regn'
        size = len(info_bytes) + len(body_bytes)
        binary = struct.pack(fmt_str, header, size, info_bytes, body_bytes)
        total_size = ser.get_padded_len(size + 8)
        return total_size, binary
