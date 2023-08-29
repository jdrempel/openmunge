import math
from typing import Iterable


class Vector3:
    __slots__ = 'x', 'y', 'z'

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def zero(cls):
        return cls()

    @classmethod
    def ones(cls):
        return cls(1.0, 1.0, 1.0)

    def __str__(self):
        return 'Vector3<{0.x}, {0.y}, {0.z}>'.format(self)

    def __repr__(self):
        return str(self)

    def __abs__(self):
        return Vector3(abs(self.x), abs(self.y), abs(self.z))

    def __add__(self, other):
        return Vector3(self.x+other.x, self.y+other.y, self.z+other.z)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z

    def __sub__(self, other):
        return Vector3(self.x-other.x, self.y-other.y, self.z-other.z)

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z

    def __mul__(self, other):
        if isinstance(other, float):
            return Vector3(other*self.x, other*self.y, other*self.z)
        return Vector3(self.x*other.x, self.y*other.y, self.z*other.z)

    def __imul__(self, other):
        if isinstance(other, float):
            self.x *= other
            self.y *= other
            self.z *= other
        else:
            self.x *= other.x
            self.y *= other.y
            self.z *= other.z

    def __truediv__(self, other):
        if isinstance(other, float):
            return Vector3(self.x/other, self.y/other, self.z/other)
        return Vector3(self.x/other.x, self.y/other.y, self.z/other.z)

    def __itruediv__(self, other):
        if isinstance(other, float):
            self.x /= other
            self.y /= other
            self.z /= other
        else:
            self.x /= other.x
            self.y /= other.y
            self.z /= other.z

    def dot(self, other) -> float:
        return self.x*other.x + self.y*other.y + self.z*other.z

    def cross(self, other):
        v0 = self.y*other.z - other.y*self.z
        v1 = self.z*other.x - other.z*self.x
        v2 = self.x*other.y - other.x*self.y
        return Vector3(v0, v1, v2)

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalized(self):
        # noinspection PyTypeChecker
        return self / self.magnitude()

    def flatten(self):
        return self.x, self.y, self.z


class Vector4:
    __slots__ = 'w', 'x', 'y', 'z'

    def __init__(self, w: float = 0.0, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def zero(cls):
        return cls()

    @classmethod
    def ones(cls):
        return cls(1.0, 1.0, 1.0, 1.0)

    def __str__(self):
        return 'Vector4<{0.w}, {0.x}, {0.y}, {0.z}>'.format(self)

    def __repr__(self):
        return str(self)

    def __abs__(self):
        return Vector4(abs(self.w), abs(self.x), abs(self.y), abs(self.z))

    def __add__(self, other):
        return Vector4(self.w+other.w, self.x+other.x, self.y+other.y, self.z+other.z)

    def __iadd__(self, other):
        self.w += other.w
        self.x += other.x
        self.y += other.y
        self.z += other.z

    def __sub__(self, other):
        return Vector4(self.w-other.w, self.x-other.x, self.y-other.y, self.z-other.z)

    def __isub__(self, other):
        self.w -= other.w
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z

    def __mul__(self, other):
        if isinstance(other, float):
            return Vector4(other*self.w, other*self.x, other*self.y, other*self.z)
        return Vector4(self.w*other.w, self.x*other.x, self.y*other.y, self.z*other.z)

    def __imul__(self, other):
        if isinstance(other, float):
            self.w *= other
            self.x *= other
            self.y *= other
            self.z *= other
        else:
            self.w *= other.w
            self.x *= other.x
            self.y *= other.y
            self.z *= other.z

    def __truediv__(self, other):
        if isinstance(other, float):
            return Vector4(self.w/other, self.x/other, self.y/other, self.z/other)
        return Vector4(self.w/other.w, self.x/other.x, self.y/other.y, self.z/other.z)

    def __itruediv__(self, other):
        if isinstance(other, float):
            self.w /= other
            self.x /= other
            self.y /= other
            self.z /= other
        else:
            self.w /= other.w
            self.x /= other.x
            self.y /= other.y
            self.z /= other.z

    def dot(self, other) -> float:
        return self.w*other.w + self.x*other.x + self.y*other.y + self.z*other.z

    def magnitude(self):
        return math.sqrt(self.dot(self))

    def normalized(self):
        # noinspection PyTypeChecker
        return self / self.magnitude()


class Matrix33:
    __slots__ = 'r0', 'r1', 'r2'

    def __init__(self, vectors: Iterable[Vector3] = None, values: Iterable[float] = None):
        self.r0 = self.r1 = self.r2 = None
        if vectors:
            self.r0, self.r1, self.r2 = vectors
        elif values:
            self.r0, self.r1, self.r2 = list(map(Vector3, zip(*[iter(values)]*3)))

    def __str__(self):
        return 'Matrix33[{0.r0}, {0.r1}, {0.r2}]'.format(self)

    def __repr__(self):
        return 'Matrix33[{0.r0}, {0.r1}, {0.r2}]'.format(self)

    def as_vectors(self):
        return self.r0, self.r1, self.r2

    def flatten(self):
        return tuple([x for r in (self.r0, self.r1, self.r2) for x in r.flatten()])

    @classmethod
    def from_vector4(cls, vec: Vector4):
        r00 = 2 * (vec.w * vec.w + vec.x * vec.x) - 1
        r01 = 2 * (vec.x * vec.y - vec.w * vec.z)
        r02 = 2 * (vec.x * vec.z + vec.w * vec.y)
        r0 = Vector3(r00, r01, r02)

        r10 = 2 * (vec.x * vec.y + vec.w * vec.z)
        r11 = 2 * (vec.w * vec.w + vec.y * vec.y) - 1
        r12 = 2 * (vec.y * vec.z - vec.w * vec.x)
        r1 = Vector3(r10, r11, r12)

        r20 = 2 * (vec.x * vec.z - vec.w * vec.y)
        r21 = 2 * (vec.y * vec.z + vec.w * vec.x)
        r22 = 2 * (vec.w * vec.w + vec.z * vec.z) - 1
        r2 = Vector3(r20, r21, r22)

        return cls(vectors=(r0, r1, r2))
