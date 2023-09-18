from dataclasses import dataclass
from enum import IntEnum
from typing import List

from core.types.math import Vector4


@dataclass
class MaterialData:
    diffuse: Vector4
    specular: Vector4
    ambient: Vector4
    sharpness: float


class MaterialFlags(IntEnum):
    NONE = 0
    UNLIT = 1
    GLOW = 2
    BLENDED_TRANSPARENCY = 4
    DOUBLE_SIDED = 8
    HARD_EDGED_TRANSPARENCY = 16
    PER_PIXEL = 32
    ADDITIVE_TRANSPARENCY = 64
    SPECULAR = 128


class RenderType(IntEnum):
    NORMAL = 0
    GLOW = 1
    LIGHTMAP = 2
    SCROLLING = 3
    SPECULAR = 4
    GLOSS_MAP = 5
    CHROME = 6
    ANIMATED = 7
    ICE = 8
    SKY = 9
    WATER = 10
    DETAIL = 11
    TWO_SCROLL = 12
    ROTATE = 13
    GLOW_ROTATE = 14
    PLANAR_REFLECTION = 15
    GLOW_SCROLL = 16
    GLOW_2_SCROLL = 17
    CURVED_REFLECTION = 18
    NORMAL_MAP_FADE = 19
    NORMAL_MAP_INV_FADE = 20
    ICE_REFLECTION = 21
    ICE_REFRACTION = 22
    EMBOSS = 23
    WIREFRAME = 24
    ENERGY = 25
    AFTERBURNER = 26
    BUMP_MAP = 27
    BUMP_MAP_GLOSS_MAP = 28
    TELEPORTAL = 29
    MULTI_STATE = 30
    SHIELD = 31


@dataclass
class MaterialAttributes:
    flags: MaterialFlags
    render_type: RenderType
    data: tuple = (0, 0)


@dataclass
class Material:
    name: str
    data: MaterialData
    attributes: MaterialAttributes
    texture_names: List[str]
