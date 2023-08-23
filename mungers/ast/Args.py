import struct
from abc import ABC, abstractmethod

from mungers.serializers.BinarySerializer import BinarySerializer


class Arg(ABC):
    def __init__(self, value):
        self.serializer = BinarySerializer
        self.value = value
        super().__setattr__('raw_value', value)

    def __str__(self):
        return '{cls}({val})'.format(cls=self.__class__.__name__, val=self.value)

    def __repr__(self):
        return str(self)

    def __setattr__(self, key, value):
        if key == 'raw_value':
            raise AttributeError('Modifying Arg.raw_value after construction is not allowed.')
        super().__setattr__(key, value)

    @abstractmethod
    def to_binary(self) -> bytes:
        ...

    @staticmethod
    @abstractmethod
    def build(tok):
        ...

    def __bytes__(self):
        return self.to_binary()


class NumberArgFactory:
    @staticmethod
    def build(tok):
        if isinstance(tok[0], int):
            return IntArg(tok[0])
        elif isinstance(tok[0], float):
            return FloatArg(tok[0])


class IntArg(Arg):
    def __init__(self, val):
        super().__init__(int(val))

    def to_binary(self) -> bytes:
        return struct.pack('<I', self.value)

    def __int__(self):
        return int(self.value)

    @staticmethod
    def build(tok):
        inst = IntArg(tok[0])
        return inst


class FloatArg(Arg):
    def __init__(self, val):
        super().__init__(float(val))

    def to_binary(self) -> bytes:
        return struct.pack('<f', self.value)

    def __float__(self):
        return float(self.value)

    @staticmethod
    def build(tok):
        inst = FloatArg(tok[0])
        return inst


class StrArg(Arg):
    def __init__(self, value):
        super().__init__(value)
        self.value = str(value)

    def to_binary(self) -> bytes:
        annotated_padded_value = struct.pack(
            '<II{}s'.format(len(self.value)+1),
            4, len(self.value)+1, bytes(self.value, encoding='ascii'))
        return annotated_padded_value

    def to_binary_no_annotation(self, strict=False) -> bytes:
        if not strict:
            return struct.pack('<I{}s'.format(len(self.value)+1), len(self.value)+1, bytes(self.value, encoding='ascii'))
        return struct.pack('<{}s'.format(len(self.value)+1), bytes(self.value, encoding='ascii'))

    def __repr__(self):
        return '{cls}({val})'.format(cls=self.__class__.__name__, val=self.value)

    def __str__(self):
        return str(self.value)

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    @staticmethod
    def build(tok):
        inst = StrArg(tok[0])
        return inst
