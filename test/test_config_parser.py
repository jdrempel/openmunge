import pathlib
import unittest
from parameterized import parameterized

from mungers.util.config_parser import *


class ConfigParserTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data_dir = self.get_data_dir('data')

    @staticmethod
    def get_data_dir(path) -> pathlib.Path:
        return pathlib.Path(__file__).parent / path

    @parameterized.expand([
        ('path config file', 'path.pth',),
        ('region config file', 'region.rgn',),
    ])
    def test_parse_config_file(self, _, filename):
        """
        This is just a simple check to make sure there are no parse errors raised while parsing.
        The correctness of the parse results will be judged in a higher-level test.
        """
        data_file = self.data_dir / filename
        parse_result = parse_config_file(data_file).as_list()
        self.assertIsInstance(parse_result, list)
        self.assertNotEqual(len(parse_result), 0)

    @parameterized.expand([
        ('Path',),
        ('Properties',),
    ])
    def test_name_parsing(self, string):
        result = name.parse_string(string)
        self.assertTrue(hasattr(result, 'name'))
        self.assertEqual(result.name, string)

    @parameterized.expand([
        ('0', int),
        ('1', int),
        ('-1', int),
        ('1.0001', float),
        ('-0.2001', float),
        ('1E5', float),
        ('"Hermite"', str),
        ('"Hello, world!"', str),
    ])
    def test_value_parsing(self, string, type_):
        result = value.parse_string(string)
        self.assertIsInstance(result[0], type_)

    @parameterized.expand([
        ('7', (int,)),
        ('7,1.0', (int, float)),
        ('7, 1.0', (int, float)),
        ('"thing", 1e4, 22', (str, float, int)),
    ])
    def test_args_parsing(self, string, types):
        result = args.parse_string(string)
        for i, parsed_arg in enumerate(result):
            self.assertIsInstance(parsed_arg, types[i])

    @parameterized.expand([
        ('Empty()', 'Empty', []),
        ('PosInt(1)', 'PosInt', [1]),
        ('NegInt(-2)', 'NegInt', [-2]),
        ('Float(3.14)', 'Float', [3.14]),
        ('EngNot(1.2E-5)', 'EngNot', [1.2e-5]),
        ('IntFloat(1, 2.0)', 'IntFloat', [1, 2.0]),
        ('FloatStr(2.0, "Things")', 'FloatStr', [2.0, 'Things']),
    ])
    def test_definition_parsing(self, string, def_name, def_args):
        result = definition.parse_string(string)
        self.assertSequenceEqual(result.name, def_name)
        self.assertListEqual(result.args.as_list(), def_args)
