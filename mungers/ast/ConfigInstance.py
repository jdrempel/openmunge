from contextlib import contextmanager

from core.util.hashing import magic
from mungers.ast.Args import Arg, FloatArg, StrArg
from mungers.chunks.Chunk import Chunk
from util.config import get_global_args
from util.constants import ALL_PLATFORMS
from util.string_util import strcmp_i


class ConfigInstance(Chunk):
    def __init__(self, name, args):
        super().__init__('DATA')
        self.name = magic(name)
        if all([not isinstance(x, Arg) for x in args]):
            self.args = [FloatArg(x) if isinstance(x, (int, float)) else StrArg(x) for x in args]
        else:
            self.args = args
        self.body = None

    def __repr__(self):
        rv = '{name}({args})'.format(name=self.name, args=', '.join(list(map(str, self.args))))
        if self.body is not None:
            rv += '[{}]'.format(len(self.body))
        return rv

    def __str__(self):
        return repr(self)

    @staticmethod
    def _build_impl(tok, force_body=False):
        tok = tok[0]
        try:
            args = tok.args.as_list()
        except AttributeError:
            args = tok.args or []
        inst = ConfigInstance(tok.name, args)
        if tok.body:
            args = get_global_args()
            # Not as simple as just taking the body, need to expand platform conditional macros
            post_macro_body = []
            for x in tok.body.as_list():
                lower_name = str(x.name).lower()
                if lower_name in ALL_PLATFORMS:
                    if strcmp_i(lower_name, args.platform) and x.body is not None:
                        for child in x.body:
                            post_macro_body.append(child)
                else:
                    post_macro_body.append(x)
            inst.body = post_macro_body

        elif force_body:
            inst.body = []
        return inst

    @staticmethod
    def build_instance(tok):
        return ConfigInstance._build_impl(tok, force_body=True)

    @staticmethod
    def build_property(tok):
        return ConfigInstance._build_impl(tok, force_body=False)

    @contextmanager
    def open(self, parent=None):
        self.binary.extend(bytes(self.chunk_id, 'ascii'))
        self.binary.extend([0]*4)
        yield self
        # Don't update size here because it includes the padding, which we don't want
        while len(self.binary) % 4:
            self.binary.append(0)
        if parent is not None:
            parent.write(self.binary)

    def to_binary(self, parent):
        with self.open(parent):
            self.write_bytes(self.name)
            self.write_byte(len(self.args))
            for arg in self.args:
                self.write_bytes(arg.to_binary())
            if not len(self.args) or isinstance(self.args[-1], FloatArg):
                self.write_int(0)
            self.update_size()  # Update size here so that we don't include the padding
            while len(self.binary) % 4:
                self.binary.append(0)
        if self.body is not None:
            with Chunk('SCOP').open(parent) as scop:
                for inst in self.body:
                    inst.to_binary(scop)
