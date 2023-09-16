import pathlib
import unittest
from unittest.mock import Mock

from core.config import setup_global_config
from mungers.util.BinaryReader import BinaryReader


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        setup_global_config(Mock())
        self.data_dir = self.get_data_dir('data')

    @staticmethod
    def get_data_dir(name: str):
        return pathlib.Path(__file__).parent / name

    def test_basic_reader_setup(self):
        binary_data_bin_file = self.data_dir / 'binary_data.bin'
        with binary_data_bin_file.open('rb') as f:
            with BinaryReader(f) as root:
                self.assertEqual(root.header, None)
                self.assertEqual(root.origin, 0)
                self.assertEqual(root.start, 0)
                self.assertEqual(root.size, 40)
                self.assertEqual(root.end, 48)
                with BinaryReader(f, parent=root) as ucfb:
                    self.assertEqual(ucfb.header, 'ucfb')
                    self.assertEqual(ucfb.origin, 0)
                    self.assertEqual(ucfb.start, 8)
                    self.assertEqual(ucfb.size, 40)
                    self.assertEqual(ucfb.end, 48)
                    with BinaryReader(f, parent=ucfb) as hdr1:
                        self.assertEqual(hdr1.header, 'HDR1')
                        self.assertEqual(hdr1.origin, 8)
                        self.assertEqual(hdr1.start, 16)
                        self.assertEqual(hdr1.size, 16)
                        self.assertEqual(hdr1.end, 32)
                        with BinaryReader(f, parent=hdr1) as info:
                            self.assertEqual(info.header, 'INFO')
                            self.assertEqual(info.origin, 16)
                            self.assertEqual(info.start, 24)
                            self.assertEqual(info.size, 7)
                            self.assertEqual(info.end, 31)
                    with BinaryReader(f, parent=ucfb) as hdr2:
                        self.assertEqual(hdr2.header, 'HDR2')
                        self.assertEqual(hdr2.origin, 32)
                        self.assertEqual(hdr2.start, 40)
                        self.assertEqual(hdr2.size, 8)
                        self.assertEqual(hdr2.end, 48)

    def test_read_str(self):
        binary_data_bin_file = self.data_dir / 'binary_data.bin'
        with binary_data_bin_file.open('rb') as f:
            with BinaryReader(f) as root:
                with BinaryReader(f, parent=root) as ucfb:
                    with BinaryReader(f, parent=ucfb) as hdr1:
                        with BinaryReader(f, parent=hdr1) as info:
                            string = hdr1.read_str()
                            self.assertEqual(string, 'foobar')

    def test_read_f32(self):
        binary_data_bin_file = self.data_dir / 'binary_data.bin'
        with binary_data_bin_file.open('rb') as f:
            with BinaryReader(f) as root:
                with BinaryReader(f, parent=root) as ucfb:
                    with BinaryReader(f, parent=ucfb) as hdr1:
                        pass
                    with BinaryReader(f, parent=ucfb) as hdr2:
                        f1 = hdr2.read_f32()
                        f2 = hdr2.read_f32()
                        self.assertAlmostEqual(f1, 3.14159265, 4)
                        self.assertAlmostEqual(f2, 2.71828182, 4)

    def test_align_and_skip(self):
        binary_data_bin_file = self.data_dir / 'binary_data.bin'
        with binary_data_bin_file.open('rb') as f:
            with BinaryReader(f) as root:
                with BinaryReader(f, parent=root) as ucfb:
                    with BinaryReader(f, parent=ucfb) as hdr1:
                        with BinaryReader(f, parent=hdr1) as info:
                            hdr1.read_str()
                            self.assertEqual(info.get_position(), 31)
                            hdr1.align()
                            self.assertEqual(info.get_position(), 32)
                            hdr1.skip(-3)
                            self.assertEqual(info.get_position(), 29)
                            hdr1.align(2)
                            self.assertEqual(info.get_position(), 30)
