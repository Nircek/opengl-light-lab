import math
from dataclasses import dataclass, field
from enum import StrEnum

from OpenGL.GL import GL_CONSTANT_ATTENUATION  # type: ignore


@dataclass
class Spherical:
    """Represents spherical coordinates.

    Attributes:
        distance: Distance from the origin.
        theta: Azimuthal angle in radians.
        phi: Polar angle in radians.
    """

    distance: float
    theta: float
    phi: float

    @property
    def x(self) -> float:
        """Returns the x-coordinate in Cartesian space."""
        return self.distance * math.cos(self.theta) * math.cos(self.phi)

    @property
    def y(self) -> float:
        """Returns the y-coordinate in Cartesian space."""
        return self.distance * math.sin(self.theta)

    @property
    def z(self) -> float:
        """Returns the z-coordinate in Cartesian space."""
        return self.distance * math.cos(self.theta) * math.sin(self.phi)


class Projection(StrEnum):
    """Camera projection types."""

    ORTHOGONAL = "ortho"
    PERSPECTIVE = "persp"


class LightType(StrEnum):
    """Types of light sources."""

    POINT = "point"
    DIRECTIONAL = "directional"


@dataclass
class AppState:
    """Holds the application state."""

    camera: Spherical = field(default_factory=lambda: Spherical(3.5, 0.4, 0.8))
    """Current camera position in spherical coordinates."""
    camera_projection: Projection = Projection.PERSPECTIVE
    """Current camera projection type."""
    camera_perspective_fov: float = 60.0
    """Field of view for perspective projection."""
    camera_ortho_half_height: float = 1.0
    """Half-height for orthogonal projection."""

    current_texture: str | None = None
    """Path to the currently loaded texture, or None."""

    light_type: LightType = LightType.POINT
    """Type of the active light source."""
    light_position: tuple[float, float, float] = (0.5, 0.5, 0.5)
    """Position of the point light source (x, y, z)."""
    light_direction: tuple[float, float, float] = (-1.0, -1.0, -1.0)
    """Direction vector of the directional light source (x, y, z)."""

    light_diffuse: tuple[float, float, float] = (1.0, 1.0, 1.0)
    """Diffuse color of the light (r, g, b)."""
    light_ambient: tuple[float, float, float] = (0.2, 0.2, 0.2)
    """Ambient color of the light (r, g, b)."""
    light_specular: tuple[float, float, float] = (1.0, 1.0, 1.0)
    """Specular color of the light (r, g, b)."""

    light_attenuation_mode: int = GL_CONSTANT_ATTENUATION
    """OpenGL attenuation mode constant."""
    light_attenuation_value: float = 1.0
    """Attenuation factor value."""
    light_model_local_viewer: bool = True
    """Whether to use local viewer lighting model."""
    light_model_two_side: bool = True
    """Whether to use two-sided lighting model."""

    rotation_angle: float = 0.0
    """Current rotation angle of the scene objects."""
    auto_rotate: bool = True
    """Whether objects should rotate automatically."""
    cube_distance: float = 1.5
    """Distance of side objects from the center."""

    show_axis: bool = False
    """Whether to draw coordinate axes."""
    show_light_position: bool = True
    """Whether to draw the light source marker."""
    lighting_enabled: bool = True
    """Whether lighting is enabled."""
    depth_test: bool = True
    """Whether depth testing is enabled."""
    show_help: bool = True
    """Whether to show the help overlay."""
