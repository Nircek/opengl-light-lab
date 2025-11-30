from OpenGL.GL import GL_QUADS, glBegin, glColor3f, glEnd, glNormal3f, glTexCoord2f, glVertex3f  # type: ignore
from OpenGL.GLU import (  # type: ignore
    GLU_FLAT,
    GLU_INSIDE,
    GLU_OUTSIDE,
    gluCylinder,
    gluDeleteQuadric,
    gluNewQuadric,
    gluQuadricNormals,
    gluQuadricOrientation,
)

# Cube vertex data: (normal, vertices for quad)
CUBE_FACES = [
    # front (+Z)
    ((0.0, 0.0, 1.0), [(-0.5, -0.5, +0.5), (+0.5, -0.5, +0.5), (+0.5, +0.5, +0.5), (-0.5, +0.5, +0.5)]),
    # back (-Z)
    ((0.0, 0.0, -1.0), [(-0.5, -0.5, -0.5), (-0.5, +0.5, -0.5), (+0.5, +0.5, -0.5), (+0.5, -0.5, -0.5)]),
    # left (-X)
    ((-1.0, 0.0, 0.0), [(-0.5, -0.5, -0.5), (-0.5, -0.5, +0.5), (-0.5, +0.5, +0.5), (-0.5, +0.5, -0.5)]),
    # right (+X)
    ((1.0, 0.0, 0.0), [(+0.5, -0.5, -0.5), (+0.5, +0.5, -0.5), (+0.5, +0.5, +0.5), (+0.5, -0.5, +0.5)]),
    # top (+Y)
    ((0.0, 1.0, 0.0), [(-0.5, +0.5, -0.5), (-0.5, +0.5, +0.5), (+0.5, +0.5, +0.5), (+0.5, +0.5, -0.5)]),
    # bottom (-Y)
    ((0.0, -1.0, 0.0), [(-0.5, -0.5, -0.5), (+0.5, -0.5, -0.5), (+0.5, -0.5, +0.5), (-0.5, -0.5, +0.5)]),
]

# Face colors for non-textured cube
CUBE_FACE_COLORS = [
    (0.0, 0.0, 1.0),  # front - blue
    (0.0, 0.0, 1.0),  # back - blue
    (1.0, 0.0, 0.0),  # left - red
    (1.0, 0.0, 0.0),  # right - red
    (0.0, 1.0, 0.0),  # top - green
    (0.0, 1.0, 0.0),  # bottom - green
]

# Texture coordinates for each face
CUBE_TEX_COORDS = [
    [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)],  # front
    [(1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)],  # back
    [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)],  # left
    [(1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)],  # right
    [(0.0, 1.0), (0.0, 0.0), (1.0, 0.0), (1.0, 1.0)],  # top
    [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)],  # bottom
]


def draw_cube() -> None:
    glBegin(GL_QUADS)
    for (normal, vertices), color in zip(CUBE_FACES, CUBE_FACE_COLORS, strict=True):
        glColor3f(*color)
        glNormal3f(*normal)
        for vertex in vertices:
            glVertex3f(*vertex)
    glEnd()


def draw_textured_cube() -> None:
    glColor3f(1.0, 1.0, 1.0)  # White to show texture colors properly
    glBegin(GL_QUADS)
    for (normal, vertices), tex_coords in zip(CUBE_FACES, CUBE_TEX_COORDS, strict=True):
        glNormal3f(*normal)
        for vertex, tex_coord in zip(vertices, tex_coords, strict=True):
            glTexCoord2f(*tex_coord)
            glVertex3f(*vertex)
    glEnd()


def draw_cylinder(*, inside: bool = False) -> None:
    glColor3f(1.0, 1.0, 0.0)
    quad = gluNewQuadric()
    gluQuadricOrientation(quad, GLU_INSIDE if inside else GLU_OUTSIDE)
    gluQuadricNormals(quad, GLU_FLAT)
    gluCylinder(quad, 0.5, 0.2, 1.0, 30, 10)
    gluDeleteQuadric(quad)


def draw_quad(size: float) -> None:
    glBegin(GL_QUADS)
    glVertex3f(-size, -size, 0.0)
    glVertex3f(+size, -size, 0.0)
    glVertex3f(+size, +size, 0.0)
    glVertex3f(-size, +size, 0.0)
    glEnd()
