import pathlib
import unittest

from mungers.parsers.OdfParser import OdfParser


class OdfParserTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data_dir = self.get_data_dir('data')
        self.parser = OdfParser()

    @staticmethod
    def get_data_dir(path) -> pathlib.Path:
        return pathlib.Path(__file__).parent / path

    def test_parse_odf_file(self):
        data_file = self.data_dir / 'object.odf'
        parse_result = self.parser.parse_file(data_file)
        expected_result = {
            '__class_name': ('foobar', False),
            'GameObjectClass': [
                ('GeometryName', 'some_thing_else.msh')
            ],
            'Properties': [
                ('Lighting', 'Dynamic'),
                ('GeometryName', 'some_thing_else'),
                ('CarriedColorize', '1'),
                ('LifeSpan', '50.0')
            ],
            'InstanceProperties': [],
        }
        self.assertDictEqual(parse_result, expected_result)

    def test_parse_odf_file_duplicates(self):
        data_file = self.data_dir / 'object_with_duplicates.odf'
        parse_result = self.parser.parse_file(data_file)
        expected_result = {
            '__class_name': ('foobar', False),
            'GameObjectClass': [],
            'Properties': [
                ('Lighting', 'Dynamic'),
                ('Lighting', 'Static'),
                ('Lighting', 'None'),
            ]
        }
        self.assertDictEqual(parse_result, expected_result)

    def test_parse_odf_file_class_parent(self):
        data_file = self.data_dir / 'object_with_parent.odf'
        parse_result = self.parser.parse_file(data_file)
        expected_result = {
            '__class_name': ('foobar', True),
            'GameObjectClass': [],
            'Properties': [
                ('Lighting', 'Dynamic'),
            ]
        }
        self.assertDictEqual(parse_result, expected_result)
