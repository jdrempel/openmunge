import math
import unittest

from core.types.math import Vector2, Vector3


class Vector2Test(unittest.TestCase):
    def assert_vecs_equal(self, v1, v2):
        self.assertAlmostEqual(v1.x, v2.x, places=5)
        self.assertAlmostEqual(v1.y, v2.y, places=5)

    def test_constructors(self):
        blank = Vector2()
        self.assertEqual(blank.x, 0)
        self.assertEqual(blank.y, 0)

        zero_explicit = Vector2(0, 0)
        self.assert_vecs_equal(blank, zero_explicit)

        zeros = Vector2.zero()
        self.assert_vecs_equal(zeros, zero_explicit)

        ones = Vector2.ones()
        one_explicit = Vector2(1, 1)
        self.assertEqual(ones.x, 1)
        self.assertEqual(ones.y, 1)

        self.assert_vecs_equal(ones, one_explicit)

    def test_abs(self):
        v1 = Vector2(-1, -1)
        self.assert_vecs_equal(abs(v1), Vector2.ones())

        v2 = Vector2.zero()
        self.assert_vecs_equal(abs(v2), Vector2.zero())

        v3 = Vector2.ones()
        self.assert_vecs_equal(abs(v3), Vector2.ones())

    def test_neg(self):
        v1 = Vector2.ones()
        self.assert_vecs_equal(-v1, Vector2(-1, -1))

    def test_add(self):
        v1 = Vector2.zero()
        v2 = Vector2(2, 3)
        self.assert_vecs_equal(v1 + v2, Vector2(2, 3))

        v3 = Vector2(4, -1)
        v4 = Vector2(-7, 3)
        self.assert_vecs_equal(v3 + v4, Vector2(-3, 2))

    def test_iadd(self):
        v1 = Vector2.zero()
        v1 += Vector2(-1, 12)
        self.assert_vecs_equal(v1, Vector2(-1, 12))

        v1 += Vector2(7, 3)
        self.assert_vecs_equal(v1, Vector2(6, 15))

    def test_sub(self):
        v1 = Vector2.zero()
        v2 = Vector2(2, 3)
        self.assert_vecs_equal(v1 - v2, Vector2(-2, -3))

        v3 = Vector2(4, -1)
        v4 = Vector2(-7, 3)
        self.assert_vecs_equal(v3 - v4, Vector2(11, -4))

    def test_isub(self):
        v1 = Vector2.zero()
        v1 -= Vector2(-1, 12)
        self.assert_vecs_equal(v1, Vector2(1, -12))

        v1 -= Vector2(7, 3)
        self.assert_vecs_equal(v1, Vector2(-6, -15))

    def test_mul(self):
        v1 = Vector2.zero()
        v2 = Vector2(8, 6)
        self.assert_vecs_equal(v1 * v2, Vector2.zero())

        v3 = Vector2.ones()
        v4 = Vector2(8, 6)
        self.assert_vecs_equal(v3 * v4, v4)

        v5 = Vector2(6, 6)
        v6 = Vector2(-1, 2)
        self.assert_vecs_equal(v5 * v6, Vector2(-6, 12))

        self.assert_vecs_equal(v5 * 4, Vector2(24, 24))

    def test_imul(self):
        v1 = Vector2.ones()
        v1 *= Vector2(2, 2)
        self.assert_vecs_equal(v1, Vector2(2, 2))

        v1 *= 17.0
        self.assert_vecs_equal(v1, Vector2(34, 34))

        v1 *= 2
        self.assert_vecs_equal(v1, Vector2(68, 68))

        v1 *= 0.25
        self.assert_vecs_equal(v1, Vector2(17, 17))

    def test_truediv(self):
        v1 = Vector2.zero()
        v2 = Vector2(8, 6)
        self.assert_vecs_equal(v1 / v2, Vector2.zero())

        v3 = Vector2.ones()
        v4 = Vector2(8, 6)
        self.assert_vecs_equal(v3 / v4, Vector2(1/8, 1/6))

        v5 = Vector2(6, 6)
        v6 = Vector2(-1, 2)
        self.assert_vecs_equal(v5 / v6, Vector2(-6, 3))

        self.assert_vecs_equal(v5 / 3, Vector2(2, 2))

    def test_itruediv(self):
        v1 = Vector2.ones()
        v1 /= Vector2(2, 2)
        self.assert_vecs_equal(v1, Vector2(0.5, 0.5))

        v1 /= 0.25
        self.assert_vecs_equal(v1, Vector2(2, 2))

        v1 /= 2
        self.assert_vecs_equal(v1, Vector2(1, 1))

        v1 /= 0.125
        self.assert_vecs_equal(v1, Vector2(8, 8))

    def test_dot(self):
        self.assertEqual(Vector2.zero().dot(Vector2.ones()), 0.0)
        self.assertEqual(Vector2.ones().dot(Vector2.ones()), 2.0)
        self.assertEqual(Vector2(3, 4).dot(Vector2(5, 6)), 39.0)
        self.assertEqual(Vector2(-0.5, 11).dot(Vector2(5, 2)), 19.5)

    def test_magnitude(self):
        self.assertEqual(Vector2.zero().magnitude(), 0.0)
        self.assertEqual(Vector2.ones().magnitude(), math.sqrt(2))
        self.assertEqual(Vector2(0, 3).magnitude(), 3.0)
        self.assertEqual(Vector2(2, 0).magnitude(), 2.0)
        self.assertEqual(Vector2(3, 4).magnitude(), 5.0)

    def test_normalized(self):
        self.assert_vecs_equal(Vector2.ones().normalized(), Vector2(math.sqrt(2), math.sqrt(2))/2)
        self.assert_vecs_equal(Vector2(18.2, 0.0).normalized(), Vector2(1, 0))
        self.assert_vecs_equal(Vector2(0, 3).normalized(), Vector2(0, 1))
        self.assert_vecs_equal(Vector2(0, -3).normalized(), Vector2(0, -1))

    def test_flatten(self):
        self.assertTupleEqual(Vector2.zero().flatten(), (0.0, 0.0))
        self.assertTupleEqual(Vector2.ones().flatten(), (1.0, 1.0))
        self.assertTupleEqual(Vector2(3.14, 2.71).flatten(), (3.14, 2.71))


class Vector3Test(unittest.TestCase):
    def assert_vecs_equal(self, v1, v2):
        self.assertAlmostEqual(v1.x, v2.x, places=5)
        self.assertAlmostEqual(v1.y, v2.y, places=5)
        self.assertAlmostEqual(v1.z, v2.z, places=5)

    def test_cross(self):
        self.assert_vecs_equal(Vector3.zero().cross(Vector3.zero()), Vector3.zero())
        self.assert_vecs_equal(Vector3.zero().cross(Vector3.ones()), Vector3.zero())
        self.assert_vecs_equal(Vector3.ones().cross(Vector3.zero()), Vector3.zero())
        self.assert_vecs_equal(Vector3.ones().cross(Vector3.ones()), Vector3.zero())

        self.assert_vecs_equal(Vector3(1, 0, 0).cross(Vector3(0, 1, 0)), Vector3(0, 0, 1))
        self.assert_vecs_equal(Vector3(0, 1, 0).cross(Vector3(1, 0, 0)), Vector3(0, 0, -1))
        self.assert_vecs_equal(Vector3(0, 0, 1).cross(Vector3(0, 1, 0)), Vector3(-1, 0, 0))
        self.assert_vecs_equal(Vector3(1, 0, 0).cross(Vector3(0, 0, 1)), Vector3(0, -1, 0))
        self.assert_vecs_equal(Vector3(0, 1, 0).cross(Vector3(0, 0, 1)), Vector3(1, 0, 0))
        self.assert_vecs_equal(Vector3(0, 0, 1).cross(Vector3(1, 0, 0)), Vector3(0, 1, 0))


class Vector4Test(unittest.TestCase):
    pass
