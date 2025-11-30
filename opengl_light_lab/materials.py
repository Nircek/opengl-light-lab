from OpenGL.GL import (  # type: ignore
    GL_AMBIENT,
    GL_DIFFUSE,
    GL_FRONT,
    GL_FRONT_AND_BACK,
    GL_SHININESS,
    GL_SPECULAR,
    GLfloat,
    glMaterialfv,
)


def setup_material(
    *,
    ambient: tuple[float, float, float, float],
    diffuse: tuple[float, float, float, float],
    specular: tuple[float, float, float, float],
    shininess: float,
    two_sided: bool = False,
) -> None:
    face = GL_FRONT_AND_BACK if two_sided else GL_FRONT
    glMaterialfv(face, GL_AMBIENT, (GLfloat * 4)(*ambient))
    glMaterialfv(face, GL_DIFFUSE, (GLfloat * 4)(*diffuse))
    glMaterialfv(face, GL_SPECULAR, (GLfloat * 4)(*specular))
    glMaterialfv(face, GL_SHININESS, (GLfloat * 1)(shininess))


def setup_material_red() -> None:
    """Red material with moderate specularity."""
    setup_material(
        ambient=(0.3, 0.1, 0.1, 1.0), diffuse=(0.8, 0.3, 0.3, 1.0), specular=(0.8, 0.8, 0.8, 1.0), shininess=50.0
    )


def setup_material_blue() -> None:
    """Blue material with high specularity."""
    setup_material(
        ambient=(0.1, 0.1, 0.3, 1.0), diffuse=(0.2, 0.4, 0.8, 1.0), specular=(1.0, 1.0, 1.0, 1.0), shininess=90.0
    )


def setup_material_green() -> None:
    """Green matte material (no specularity)."""
    setup_material(
        ambient=(0.1, 0.3, 0.1, 1.0),
        diffuse=(0.3, 0.7, 0.3, 1.0),
        specular=(0.0, 0.0, 0.0, 1.0),
        shininess=0.0,
        two_sided=True,
    )


def setup_material_white() -> None:
    """White/neutral material for textured surfaces."""
    setup_material(
        ambient=(1.0, 1.0, 1.0, 1.0), diffuse=(1.0, 1.0, 1.0, 1.0), specular=(0.3, 0.3, 0.3, 1.0), shininess=20.0
    )
