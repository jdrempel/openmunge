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

    def write_str_fixed(self, string, length):
        str_bytes = bytes(str(string), 'ascii') + b'\x00'
        if len(str_bytes) > length:
            str_bytes = str_bytes[:length-1]
        while len(str_bytes) < length:
            str_bytes += b'\x00'
        self.binary.extend(str_bytes)

    def write_byte(self, num):
        packed = struct.pack('<B', num)
        self.binary.extend(packed)

    def write_short(self, num):
        packed = struct.pack('<H', int(num))
        self.binary.extend(packed)

    def write_bytes(self, data):
        self.binary.extend(data)

    def write_int(self, num):
        packed = struct.pack('<I', int(num))
        self.binary.extend(packed)

    def write_float(self, num):
        packed = struct.pack('<f', float(num))
        self.binary.extend(packed)

    def write_vec2(self, vec):
        packed = struct.pack('<2f', *vec.flatten())
        self.binary.extend(packed)

    def write_vec3(self, vec):
        packed = struct.pack('<3f', *vec.flatten())
        self.binary.extend(packed)

    def write_vec4(self, vec):
        packed = struct.pack('<4f', *vec.flatten())
        self.binary.extend(packed)

    def write_quat(self, quat):
        packed = struct.pack('<4f', quat.x, quat.y, quat.z, quat.w)
        self.binary.extend(packed)

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
