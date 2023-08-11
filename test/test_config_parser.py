import argparse
import pathlib
import unittest
from parameterized import parameterized

from mungers.util.config_parser import *
from util.config import setup_global_args, setup_global_config


class ConfigParserTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data_dir = self.get_data_dir('data')
        setup_global_config()
        setup_global_args(argparse.Namespace(platform='pc'))

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
        parse_result = parse_config_file(data_file)
        self.assertIsInstance(parse_result, Config)

    @parameterized.expand([
        ('Path',),
        ('Properties',),
    ])
    def test_name_parsing(self, string):
        result = name.parse_string(string)
        self.assertTrue(hasattr(result, 'name'))
        self.assertEqual(result.name, string)

    @parameterized.expand([
        ('0', FloatArg),
        ('1', FloatArg),
        ('-1', FloatArg),
        ('1.0001', FloatArg),
        ('-0.2001', FloatArg),
        ('1E5', FloatArg),
        ('"Hermite"', StrArg),
        ('"Hello, world!"', StrArg),
    ])
    def test_value_parsing(self, string, type_):
        result = value.parse_string(string)
        self.assertIsInstance(result[0], type_)

    @parameterized.expand([
        ('7', (FloatArg,)),
        ('7,1.0', (FloatArg, FloatArg)),
        ('7, 1.0', (FloatArg, FloatArg)),
        ('"thing", 1e4, 22', (StrArg, FloatArg, FloatArg)),
    ])
    def test_args_parsing(self, string, types):
        result = args.parse_string(string)
        for i, parsed_arg in enumerate(result):
            self.assertIsInstance(parsed_arg, types[i])

    @parameterized.expand([
        ('Empty()', 'Empty', []),
        ('PosInt(1)', 'PosInt', [1.0]),
        ('NegInt(-2)', 'NegInt', [-2.0]),
        ('Float(3.14)', 'Float', [3.14]),
        ('EngNot(1.2E-5)', 'EngNot', [1.2e-5]),
        ('IntFloat(1, 2.0)', 'IntFloat', [1.0, 2.0]),
        ('FloatStr(2.0, "Things")', 'FloatStr', [2.0, 'Things']),
    ])
    def test_definition_parsing(self, string, def_name, def_args):
        result = definition.parse_string(string)
        self.assertSequenceEqual(result.name, def_name)
        self.assertSequenceEqual([arg.value for arg in result.args], def_args)

    @parameterized.expand([
        ('Prop0Args();', [], None),
        ('Prop1Arg(1);', [1.0], None),
        ('Prop2Args(1, 2);', [1.0, 2.0], None),
        ('Instance0ArgsEmpty() { }', [], []),
        ('Instance1ArgEmpty("FOOBAR") { }', ['FOOBAR'], []),
        ('Instance0ArgsSingle() { Nested(0); }', [], [([0.0], None)]),
        ('Instance1ArgSingle("FOOBAR") { Nested(0); }', ['FOOBAR'], [([0.0], None)]),
    ])
    def test_instance_parsing(self, string, args_, body):
        result = instance.parse_string(string)[0]
        self.assertIsInstance(result, ConfigInstance)
        self.assertTrue(bool(result.name))
        self.assertListEqual([arg.value for arg in result.args], args_)
        if body:
            self.assertNotEqual(len(result.body), 0)
            for i, nested in enumerate(body):
                self.assertListEqual([arg.value for arg in result.body[i].args], nested[0])
