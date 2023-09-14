import unittest

from mungers.ast.ConfigInstance import ConfigInstance


class AstNodesTest(unittest.TestCase):
    def setUp(self) -> None:
        pass

    @staticmethod
    def test_ConfigInstance_repr():
        ci = ConfigInstance('foo', [1, 2, 3])
        repr(ci)
