import struct

FNV_PRIME = 16777619
OFFSET_BASIS = 2166136261
U32_MASK = 2**32-1


def fnv1a_hash(buffer: bytes) -> bytes:
    result = OFFSET_BASIS
    for byte in buffer:
        result = (result ^ (byte | 0x20)) & U32_MASK
        result = (result * FNV_PRIME) & U32_MASK
    return struct.pack('<I', result)
