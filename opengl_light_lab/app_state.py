import math
from dataclasses import dataclass, field
from enum import StrEnum

from OpenGL.GL import GL_CONSTANT_ATTENUATION  # type: ignore


@dataclass
class Spherical:
    distance: float
    theta: float
    phi: float

    @property
    def x(self) -> float:
        return self.distance * math.cos(self.theta) * math.cos(self.phi)

    @property
    def y(self) -> float:
        return self.distance * math.sin(self.theta)

    @property
    def z(self) -> float:
        return self.distance * math.cos(self.theta) * math.sin(self.phi)


class Projection(StrEnum):
    ORTHOGONAL = "ortho"
    PERSPECTIVE = "persp"


@dataclass
class AppState:
    camera: Spherical = field(default_factory=lambda: Spherical(3.5, 0.4, 0.8))
    camera_projection: Projection = Projection.PERSPECTIVE
    camera_perspective_fov: float = 60.0
    camera_ortho_half_height: float = 1.0

    light_x: float = 0.5
    light_y: float = 0.5
    light_z: float = 0.5

    light_attenuation_mode: int = GL_CONSTANT_ATTENUATION
    light_attenuation_value: float = 1.0
    light_model_local_viewer: bool = False
    light_model_two_side: bool = False

    rotation_angle: float = 0.0
    auto_rotate: bool = True
    cube_distance: float = 1.5

    show_axis: bool = False
    show_light_position: bool = True
    lighting_enabled: bool = True
    depth_test: bool = True
    show_help: bool = True
