import struct

from core.util.hashing import fnv1a_hash
from mungers.ast.Args import Arg, FloatArg, StrArg
from mungers.ast.AstNode import AstNode
from mungers.serializers.BinarySerializer import BinarySerializer


class ConfigInstance(AstNode):
    def __init__(self, name, args):
        self.name = name
        if all([not isinstance(x, Arg) for x in args]):
            self.args = [FloatArg(x) if isinstance(x, (int, float)) else StrArg(x) for x in args]
        else:
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
        arg_fmt_str = 'B'
        #args_bytes.extend([nargs])

        first = True
        args_size = 0
        for arg in self.args:
            arg_binary = arg.to_binary()
            args_bytes.extend(arg_binary)
            arg_size = len(arg_binary)
            #if first:
            #    first = False
            #    arg_size += 1
            args_size += arg_size
        if args_size:
            if isinstance(self.args[-1], FloatArg):  # Heuristic, not sure if you can have combinations of str, float
                args_bytes.extend(b'\x00'*4)
                args_size += 4
            arg_fmt_str += '{}s'.format(args_size)
        else:
            args_bytes.extend(b'\x00'*4)
            args_size += 4
            arg_fmt_str += '{}s'.format(args_size)
        fmt_str += arg_fmt_str
        arg_padding = ser.get_padded_len(len(args_bytes)+1) - len(args_bytes) - 1  # -1 to account for nargs
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
        size = len(name) + len(args_bytes) + 1
        if self.body is not None:
            #size += len(body_bytes)
            if len(body_bytes):
                binary = struct.pack(fmt_str, header, size, name, nargs, args_bytes, body_bytes)
            else:
                binary = struct.pack(fmt_str, header, size, name, nargs, args_bytes)
        else:
            binary = struct.pack(fmt_str, header, size, name, nargs, args_bytes)
        total_size = ser.get_padded_len(size + 8)
        return total_size, binary
