import unittest

from parameterized import parameterized

from mungers.util.req_parser import *


class ReqParserTest(unittest.TestCase):
    def setUp(self) -> None:
        pass

    @parameterized.expand([
        ('empty', '""'),
        ('one char', '"a"'),
        ('one word', '"apple"'),
        ('underscores', '"apple_banana"'),
        ('multi word', '"apple banana"'),
    ])
    def test_header_parsing(self, _name, string):
        result = header.parse_string(string)
        self.assertSequenceEqual(result[0], string.strip('"'))

    @parameterized.expand([
        ('empty', '""'),
        ('one char', '"a"'),
        ('one word', '"apple"'),
        ('underscores', '"apple_banana"'),
        ('multi word', '"apple banana"'),
    ])
    def test_entry_parsing(self, _name, string):
        result = entry.parse_string(string)
        self.assertSequenceEqual(result[0], string.strip('"'))

    @parameterized.expand([
        ('empty list', '"header"\n', ['header', []]),
        ('single entry list', '"header"\n"item_1"', ['header', ['item_1']]),
        ('multi entry list', '"header"\n"item_1"\n"item_2"', ['header', ['item_1', 'item_2']]),
    ])
    def test_entries_parsing(self, _name, string, expected):
        result = entries.parse_string(string).as_list()
        self.assertListEqual(result, expected)

    @parameterized.expand([
        ('empty section', 'REQN { "config" }', ReqList('config', [])),
        ('section with one entry', 'REQN { "config"\n"item_1" }', ReqList('config', ['item_1'])),
        ('section with two entries', 'REQN { "config"\n"item_1"\n"item_2" }',
         ReqList('config', ['item_1', 'item_2'])),
        ('section with many entries', 'REQN { "config"\n"item_1"\n"item_2"\n"item_3"\n"item_4"\n"item_5" }',
         ReqList('config', ['item_1', 'item_2', 'item_3', 'item_4', 'item_5'])),
    ])
    def test_section_parsing(self, _name, string, expected):
        result = section.parse_string(string)[0]
        self.assertEqual(result.header, expected.header)
        self.assertListEqual(result.entries, expected.entries)

    @parameterized.expand([
        ('empty doc', 'ucft { }'),
        ('doc with one section', 'ucft { REQN { "config_1"\n"item_1" } }'),
        ('doc with two sections', 'ucft { REQN { "config_1"\n"item_1" } REQN { "config_2"\n"item_1" } }'),
    ])
    def test_req_doc_parsing(self, _name, string):
        result = req_doc.parse_string(string)
