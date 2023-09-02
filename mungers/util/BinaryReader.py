import io
import pathlib
import struct


class BinaryReader:
    def __init__(self, path: pathlib.Path):
        self.path = path
        self._stream = None

    def __enter__(self):
        self._stream = self.path.open('rb')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stream.close()

    def read_int(self) -> int:
        data = self._stream.read(4)
        return struct.unpack('<I', data)[0]

    def read_short(self) -> int:
        data = self._stream.read(2)
        return struct.unpack('<H', data)[0]

    def read_byte(self) -> int:
        data = self._stream.read(1)
        return struct.unpack('<B', data)[0]

    def read_bytes(self, n: int) -> bytes:
        data = self._stream.read(n)
        return data

    def read_float(self) -> float:
        data = self._stream.read(4)
        return struct.unpack('<f', data)[0]

    def read_str(self) -> str:
        result = bytes()
        while True:
            byte = self._stream.read(1)
            if not byte:
                break
            result += byte
        return result.decode('ascii')

    def read_str_fixed(self, n: int) -> str:
        data = self._stream.read(n)
        return data.decode('ascii')

    def align(self, size=4) -> None:
        pos = self._stream.tell()
        dist = pos % size
        if not dist:
            return
        offset = size - dist
        self._stream.seek(offset, io.SEEK_CUR)

    def skip(self, n: int) -> None:
        self._stream.seek(n, io.SEEK_CUR)

