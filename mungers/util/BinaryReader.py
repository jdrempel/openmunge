import io
import pathlib
import struct

from core.config import get_global_config
from core.types.math import Vector3, Vector4, Matrix33
from util.logs import setup_logger


class BinaryReader:
    def __init__(self, file, parent=None):
        self.logger = setup_logger('BinaryReader', level=get_global_config().log_level)
        self.parent = parent
        self.origin = 0
        self.start = None
        self.size = 0
        self.end = None
        self.header = None

        self._stream = file

    # Context management methods

    def __enter__(self):
        self.origin = self._stream.tell()
        if self.parent is not None:
            self.header = self.read_str_fixed(4)
            self.size = self.read_u32()
            self.start = self._stream.tell()
        else:
            self.origin = 0
            self.start = 0
            self.size = pathlib.Path(self._stream.name).stat().st_size - 8

        self.end = self.origin + self.size + 8

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stream.seek(self.end)

    # Methods for reading binary data into useful Python types

    def read_bytes(self, n: int) -> bytes:
        data = self._stream.read(n)
        return data

    def read_str(self) -> str:
        result = bytes()
        while True:
            byte = self._stream.read(1)
            if not ord(byte):
                break
            result += byte
        return result.decode('ascii')

    def read_str_fixed(self, n: int) -> str:
        data = self._stream.read(n)
        return data.decode('ascii')

    def read_u8(self, n: int = 1):
        buffer = self._stream.read(n)
        result = struct.unpack(f'<{n}B', buffer)
        return result[0] if n == 1 else result

    def read_i8(self, n: int = 1):
        buffer = self._stream.read(n)
        result = struct.unpack(f'<{n}b', buffer)
        return result[0] if n == 1 else result

    def read_u16(self, n: int = 1):
        buffer = self._stream.read(2*n)
        result = struct.unpack(f'<{n}H', buffer)
        return result[0] if n == 1 else result

    def read_i16(self, n: int = 1):
        buffer = self._stream.read(2*n)
        result = struct.unpack(f'<{n}h', buffer)
        return result[0] if n == 1 else result

    def read_u32(self, n: int = 1):
        buffer = self._stream.read(4*n)
        result = struct.unpack(f'<{n}I', buffer)
        return result[0] if n == 1 else result

    def read_i32(self, n: int = 1):
        buffer = self._stream.read(4*n)
        result = struct.unpack(f'<{n}i', buffer)
        return result[0] if n == 1 else result

    def read_f32(self, n: int = 1):
        buffer = self._stream.read(4*n)
        result = struct.unpack(f'<{n}f', buffer)
        return result[0] if n == 1 else result

    def read_vec3(self):
        return Vector3(self.read_f32(3))

    def read_vec4(self):
        return Vector4(self.read_f32(4))

    def read_quat(self):
        rot = self.read_f32(4)
        return Vector4(rot[3], rot[0], rot[1], rot[2])

    def read_mat33(self):
        values = self.read_f32(3*3)
        return Matrix33(values=values)

    # Navigation methods

    def get_position(self):
        return self._stream.tell()

    def align(self, size=4) -> None:
        pos = self._stream.tell()
        dist = pos % size
        if not dist:
            return
        offset = size - dist
        self._stream.seek(offset, io.SEEK_CUR)

    def skip(self, n: int) -> None:
        self._stream.seek(n, io.SEEK_CUR)

