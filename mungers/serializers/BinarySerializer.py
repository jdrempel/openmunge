class BinarySerializer:
    U32_SZ = 4

    @staticmethod
    def get_padded_len(x: int, min_len=None):
        round_up = bool(x % BinarySerializer.U32_SZ)
        padded_len = BinarySerializer.U32_SZ * (x // BinarySerializer.U32_SZ + int(round_up))
        if min_len is not None:
            return max(padded_len, min_len)
        return padded_len
