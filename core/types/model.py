from collections import namedtuple
from dataclasses import dataclass, field
from enum import IntEnum
from typing import List

from core.types.math import Vector3, Quaternion


class ModelType(IntEnum):
    NULL = 0
    SKIN = 1
    CLOTH = 2
    BONE = 3
    STATIC = 4
    _UNUSED = 5
    SHADOW_VOLUME = 6


class CollisionPrimitiveShape(IntEnum):
    SPHERE = 0
    ELLIPSOID = 1
    CYLINDER = 2
    MESH = 3
    BOX = 4


@dataclass
class CollisionPrimitive:
    shape: CollisionPrimitiveShape
    radius: float
    height: float
    length: float


@dataclass
class ModelTransform:
    scale: Vector3
    translation: Vector3
    rotation: Quaternion


@dataclass
class BoundingBox:
    rotation: Quaternion
    origin: Vector3
    extents: Vector3
    sphere_radius: float

    @property
    def min(self):
        return self.origin - abs(self.extents)

    @property
    def max(self):
        return self.origin + abs(self.extents)


@dataclass
class SceneInfo:
    name: str
    start_frame: int = 0
    end_frame: int = 1
    frame_rate: float = 29.97003
    bounding_box: BoundingBox = field(default_factory=BoundingBox)


@dataclass
class GeometrySegment:
    material_name: str

    positions: List
    normals: List
    colours: List
    uvs: List

    weights: List

    polygons: List
    tris: List
    tri_strips: List


Geometry = namedtuple('Geometry', ('bounding_box', 'segments', 'cloth', 'envelope'))


@dataclass
class Model:
    name: str
    model_type: ModelType
    transform: ModelTransform
    geometries: List[Geometry]

    @property
    def segments(self):
        return [segment for geometry in self.geometries for segment in geometry.segments]
