import struct
from contextlib import contextmanager


class Chunk:
    def __init__(self, chunk_id: str, name: str = None):
        self._chunk_id = None
        self.chunk_id = chunk_id
        self.name = name
        self.size = 0
        self.binary = bytearray()

    @property
    def chunk_id(self):
        return self._chunk_id

    @chunk_id.setter
    def chunk_id(self, value):
        if not isinstance(value, str):
            raise TypeError('Chunk id must be a str.')
        self._chunk_id = value
        while len(self._chunk_id) % 4:
            self._chunk_id += '_'

    def update_size(self):
        self.size = len(self.binary[8:])
        self.binary[4:8] = struct.pack('<I', self.size)

    def write(self, binary):
        self.binary.extend(binary)

    def write_str(self, string):
        str_bytes = bytes(str(string), 'ascii') + b'\x00'
        self.binary.extend(str_bytes)

    def write_byte(self, num):
        num_bytes = struct.pack('<B', num)
        self.binary.extend(num_bytes)

    def write_bytes(self, data):
        self.binary.extend(data)

    def write_int(self, num):
        num_bytes = struct.pack('<I', int(num))
        self.binary.extend(num_bytes)

    def write_float(self, num):
        num_bytes = struct.pack('<f', float(num))
        self.binary.extend(num_bytes)

    @contextmanager
    def open(self, parent=None):
        self.binary.extend(bytes(self.chunk_id, 'ascii'))
        self.binary.extend([0]*4)
        yield self
        self.update_size()
        while len(self.binary) % 4:
            self.binary.append(0)
        if parent is not None:
            parent.write(self.binary)


if __name__ == '__main__':
    with Chunk('wrld').open() as world:
        with Chunk('INFO').open(world) as info:
            info.write(b'henlo')

    pass
