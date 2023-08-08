import unittest

from mungers.ast.ConfigInstance import ConfigInstance


class AstNodesTest(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_ConfigInstance_repr(self):
        ci = ConfigInstance('foo', [1, 2, 3])
        repr(ci)
