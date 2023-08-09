import struct

from core.util.hashing import fnv1a_hash
from mungers.ast.AstNode import AstNode
from mungers.serializers.BinarySerializer import BinarySerializer


class ConfigInstance(AstNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args
        self.body = None

    @staticmethod
    def _build_impl(tok, force_body=False):
        tok = tok[0]
        try:
            args = tok.args.as_list()
        except AttributeError:
            args = tok.args or []
        inst = ConfigInstance(tok.name, args)
        if tok.body:
            inst.body = tok.body.as_list()
        elif force_body:
            inst.body = []
        return inst

    @staticmethod
    def build_instance(tok):
        return ConfigInstance._build_impl(tok, force_body=True)

    @staticmethod
    def build_property(tok):
        return ConfigInstance._build_impl(tok, force_body=False)

    def __repr__(self):
        rv = '{name}({args})'.format(name=self.name, args=', '.join(list(map(str, self.args))))
        if self.body is not None:
            rv += '[{}]'.format(len(self.body))
        return rv

    def __str__(self):
        return repr(self)

    def to_binary(self):
        ser = BinarySerializer
        fmt_str = '<4sI4s'  # DATAsizehash...args...body

        nargs = len(self.args)
        args_bytes = bytearray()
        arg_fmt_str = ''
        args_bytes.extend([nargs])

        first = True
        args_size = 0
        for arg in self.args:
            arg_size = ser.serialize(arg)
            if first:
                first = False
                arg_size += 1
            if isinstance(arg, (int, float)):
                arg_ = float(arg)
                args_bytes.extend(struct.pack('<f', arg_))
            elif isinstance(arg, str):
                arg_ = bytes(arg, encoding='ascii')
                arg_len = len(arg_)+1
                padded_len = ser.get_padded_len(arg_len)
                args_bytes.extend(struct.pack('<{}s'.format(padded_len), arg_))
            args_size += arg_size
        arg_fmt_str += '{}s'.format(args_size)
        fmt_str += arg_fmt_str
        arg_padding = ser.get_padded_len(len(args_bytes), min_len=12) - len(args_bytes)
        fmt_str += 'x'*arg_padding

        body_bytes = bytearray()
        if self.body is not None:
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

        header = b'DATA'
        name = fnv1a_hash(bytes(self.name, encoding='ascii'))
        size = len(name) + ser.get_padded_len(len(args_bytes)) + 1  # +1 to account for nargs
        if self.body is not None:
            size += len(body_bytes)
            if len(body_bytes):
                binary = struct.pack(fmt_str, header, size, name, args_bytes, body_bytes)
            else:
                binary = struct.pack(fmt_str, header, size, name, args_bytes)
        else:
            binary = struct.pack(fmt_str, header, size, name, args_bytes)
        total_size = ser.get_padded_len(size + 8)
        return total_size, binary
