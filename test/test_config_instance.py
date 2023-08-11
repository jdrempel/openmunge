import struct
import unittest
from typing import Optional

from parameterized import parameterized

from mungers.ast.ConfigInstance import ConfigInstance
from mungers.serializers.BinarySerializer import BinarySerializer


class ConfigInstanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.serializer = BinarySerializer

    @parameterized.expand([
        ('empty', ConfigInstance('Foo', []), None, 20,
         b'DATA\t\x00\x00\x00\xd7~\xf3\xa9\x00\x00\x00\x00\x00\x00\x00\x00'),
        ('one int arg', ConfigInstance('Foo', [9]), None, 24,
         b'DATA\r\x00\x00\x00\xd7~\xf3\xa9\x01\x00\x00\x10A\x00\x00\x00\x00\x00\x00\x00'),
        ('one float arg', ConfigInstance('Foo', [3.14]), None, 24,
         b'DATA\r\x00\x00\x00\xd7~\xf3\xa9\x01\xc3\xf5H@\x00\x00\x00\x00\x00\x00\x00'),
        ('two float args', ConfigInstance('Foo', [3.14, 2.71]), None, 28,
         b'DATA\x11\x00\x00\x00\xd7~\xf3\xa9\x02\xc3\xf5H@\xa4p-@\x00\x00\x00\x00\x00\x00\x00'),
        ('three float args', ConfigInstance('Foo', [3.14, 2.71, 1.41]), None, 32,
         b'DATA\x15\x00\x00\x00\xd7~\xf3\xa9\x03\xc3\xf5H@\xa4p-@\xe1z\xb4?\x00\x00\x00\x00\x00\x00\x00'),
        ('one str arg', ConfigInstance('Foo', ['Hermite']), None, 32,
         b'DATA\x15\x00\x00\x00\xd7~\xf3\xa9\x01\x04\x00\x00\x00\x08\x00\x00\x00Hermite\x00\x00\x00\x00'),
        ('empty body', ConfigInstance('Foo', [3.14, 2.71, 1.41]), [], 40,
         b'DATA\x15\x00\x00\x00\xd7~\xf3\xa9\x03\xc3\xf5H@\xa4p-@\xe1z\xb4?\x00\x00\x00\x00\x00\x00\x00'
         b'SCOP\x00\x00\x00\x00'),
    ])
    def test_to_binary(self, _name: str, inst: ConfigInstance, body: Optional[list], expected_total_size: int,
                       expected_binary: bytes):
        if body is not None:
            inst.body = body
        total_size, binary = inst.to_binary()

        self.assertEqual(total_size, expected_total_size)
        self.assertSequenceEqual(binary, expected_binary)
