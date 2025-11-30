import time

from OpenGL.GL import (  # type: ignore
    GL_AMBIENT,
    GL_COLOR_BUFFER_BIT,
    GL_CONSTANT_ATTENUATION,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_DIFFUSE,
    GL_FRONT,
    GL_FRONT_AND_BACK,
    GL_LEQUAL,
    GL_LIGHT0,
    GL_LIGHT_MODEL_LOCAL_VIEWER,
    GL_LIGHT_MODEL_TWO_SIDE,
    GL_LIGHTING,
    GL_LIGHTING_BIT,
    GL_LINEAR_ATTENUATION,
    GL_LINES,
    GL_MODELVIEW,
    GL_NORMALIZE,
    GL_POSITION,
    GL_PROJECTION,
    GL_QUADRATIC_ATTENUATION,
    GL_QUADS,
    GL_SHININESS,
    GL_SMOOTH,
    GL_SPECULAR,
    GLfloat,
    glBegin,
    glClear,
    glClearColor,
    glColor3f,
    glDepthFunc,
    glDisable,
    glEnable,
    glEnd,
    glLightf,
    glLightfv,
    glLightModelf,
    glLightModeli,
    glLineWidth,
    glLoadIdentity,
    glMaterialfv,
    glMatrixMode,
    glNormal3f,
    glOrtho,
    glPopAttrib,
    glPopMatrix,
    glPushAttrib,
    glPushMatrix,
    glRotatef,
    glShadeModel,
    glTranslatef,
    glVertex3f,
    glViewport,
)
from OpenGL.GLU import (  # type: ignore
    GLU_FLAT,
    GLU_INSIDE,
    GLU_OUTSIDE,
    gluCylinder,
    gluDeleteQuadric,
    gluLookAt,
    gluNewQuadric,
    gluPerspective,
    gluQuadricNormals,
    gluQuadricOrientation,
    gluSphere,
)
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from opengl_light_lab import AppState, Projection, Spherical

HELP_TEXT = """
Controls:
  Esc       - quit
  Space     - toggle auto-rotate
  1         - toggle lighting
  2         - toggle showing light marker
  3         - toggle depth test
  4         - cycle light attenuation mode (constant/linear/quadratic)
  5         - change attenuation value (Shift+5 decreases)
  6         - toggle local viewer light model
  7         - toggle two-sided lighting model
  0         - toggle axis display
  O         - orthogonal projection
  P         - perspective projection
  UHJKYI    - move light on axes (Z +/- / X +/- / Y +/-)
  Q/E       - zoom out/in (or change ortho half-height)
  W/S/A/D   - change camera angles (theta / phi)
  [ / ]     - change FOV (perspective)
  Z/X       - change cube distance

TODO:
- animacja obrotu
- tekstura
- sterowanie światłem (wszystkie parametry)
- kilka obiektów 3d
- sterowanie obiektem, obrót kamery
- przynajmniej jedna tekstura
- światło
- GLSL
"""
FULL_REVOLUTION = 360.0


class GLWidget(QOpenGLWidget):
    def __init__(self, parent: QtWidgets.QWidget | None, app_state: AppState) -> None:
        super().__init__(parent)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.app_state = app_state
        self.last_time = time.time()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(16)  # ~60Hz
        self._dt = 0.0
        self._pressed_keys: set[str] = set()

    def initializeGL(self) -> None:
        glClearColor(0.15, 0.15, 0.18, 1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glShadeModel(GL_SMOOTH)

        glEnable(GL_NORMALIZE)

    def resizeGL(self, w: int, h: int) -> None:
        if h == 0:
            h = 1
        aspect = w / h
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        ohh = self.app_state.camera_ortho_half_height
        if self.app_state.camera_projection == Projection.ORTHOGONAL:
            glOrtho(-ohh * aspect, +ohh * aspect, -ohh, +ohh, 0.1, 100.0)
        else:
            gluPerspective(self.app_state.camera_perspective_fov, aspect, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self) -> None:
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        if self.app_state.auto_rotate:
            self._dt += dt
            self.rotation_update(self._dt)
            self._dt = 0.0

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        camera = self.app_state.camera
        north = Spherical(self.app_state.camera.distance, self.app_state.camera.theta + 0.01, self.app_state.camera.phi)
        gluLookAt(camera.x, camera.y, camera.z, 0.0, 0.0, 0.0, north.x, north.y, north.z)

        if self.app_state.depth_test:
            glEnable(GL_DEPTH_TEST)
        else:
            glDisable(GL_DEPTH_TEST)

        self.setup_light()

        if self.app_state.lighting_enabled:
            glEnable(GL_LIGHTING)
        else:
            glDisable(GL_LIGHTING)
            glColor3f(0.5, 0.5, 0.5)

        if self.app_state.lighting_enabled and self.app_state.show_light_position:
            self.draw_light_marker()

        if self.app_state.show_axis:
            self.draw_axis()

        glPushMatrix()
        glTranslatef(-self.app_state.cube_distance, 0.0, 0.0)
        glRotatef(self.app_state.rotation_angle, 0, 1, 0)
        self.setup_material_red()
        self.draw_cylinder(inside=True)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0.0, 0.0, 0.0)
        glRotatef(self.app_state.rotation_angle, 1, 0, 0)
        self.setup_material_blue()
        self.draw_raw_cube()
        glPopMatrix()

        glPushMatrix()
        glTranslatef(+self.app_state.cube_distance, 0.0, 0.0)
        glRotatef(self.app_state.rotation_angle, 0, 0, 1)
        self.setup_material_green()
        self.draw_cylinder(inside=False)
        glPopMatrix()

        if self.app_state.show_help:
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.RenderHint.TextAntialiasing)
            margin = 8
            w = min(600, self.width() - 20)
            h = min(400, self.height() - 20)
            rect = QtCore.QRect(margin, margin, w, h)
            painter.fillRect(rect, QtGui.QColor(0, 0, 0, 180))
            painter.setPen(QtGui.QColor(240, 240, 240))
            font = QtGui.QFont("", 10)
            painter.setFont(font)
            painter.drawText(rect.adjusted(8, 8, -8, -8), QtCore.Qt.TextFlag.TextWordWrap, HELP_TEXT)
            painter.end()

    def rotation_update(self, dt_seconds: float) -> None:
        self.app_state.rotation_angle += 20.0 * dt_seconds
        if self.app_state.rotation_angle > FULL_REVOLUTION:
            self.app_state.rotation_angle -= FULL_REVOLUTION

    def draw_axis(self) -> None:
        glPushAttrib(GL_LIGHTING_BIT)
        glDisable(GL_LIGHTING)
        glLineWidth(2.0)
        glBegin(GL_LINES)

        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(25.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        for i in range(1, 25):
            glVertex3f(-i, 0.0, 0.0)

        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 25.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        for i in range(1, 25):
            glVertex3f(0.0, -i, 0.0)

        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 25.0)
        glVertex3f(0.0, 0.0, 0.0)
        for i in range(1, 25):
            glVertex3f(0.0, 0.0, -i)

        glEnd()
        glPopAttrib()

    def setup_light(self) -> None:
        light_pos = (GLfloat * 4)(self.app_state.light_x, self.app_state.light_y, self.app_state.light_z, 1.0)
        light_diffuse = (GLfloat * 4)(1.0, 1.0, 1.0, 1.0)
        light_ambient = (GLfloat * 4)(0.2, 0.2, 0.2, 1.0)
        light_specular = (GLfloat * 4)(1.0, 1.0, 1.0, 1.0)

        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.0)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.0)
        glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.0)
        glLightf(GL_LIGHT0, self.app_state.light_attenuation_mode, self.app_state.light_attenuation_value)

        glLightModelf(GL_LIGHT_MODEL_LOCAL_VIEWER, 1.0 if self.app_state.light_model_local_viewer else 0.0)
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, 1 if self.app_state.light_model_two_side else 0)

    def setup_material_red(self) -> None:
        mat_ambient = (GLfloat * 4)(0.3, 0.1, 0.1, 1.0)
        mat_diffuse = (GLfloat * 4)(0.8, 0.3, 0.3, 1.0)
        mat_specular = (GLfloat * 4)(0.8, 0.8, 0.8, 1.0)
        mat_shininess = (GLfloat * 1)(50.0)
        glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)

    def setup_material_blue(self) -> None:
        mat_ambient = (GLfloat * 4)(0.1, 0.1, 0.3, 1.0)
        mat_diffuse = (GLfloat * 4)(0.2, 0.4, 0.8, 1.0)
        mat_specular = (GLfloat * 4)(1.0, 1.0, 1.0, 1.0)
        mat_shininess = (GLfloat * 1)(90.0)
        glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)

    def setup_material_green(self) -> None:
        mat_ambient = (GLfloat * 4)(0.1, 0.3, 0.1, 1.0)
        mat_diffuse = (GLfloat * 4)(0.3, 0.7, 0.3, 1.0)
        mat_specular = (GLfloat * 4)(0.0, 0.0, 0.0, 1.0)
        mat_shininess = (GLfloat * 1)(0.0)
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, mat_ambient)
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, mat_diffuse)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, mat_specular)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, mat_shininess)

    def draw_raw_cube(self) -> None:
        glBegin(GL_QUADS)

        # front (+Z)
        glColor3f(0.0, 0.0, 1.0)
        glNormal3f(0.0, 0.0, 1.0)
        glVertex3f(-0.5, -0.5, +0.5)
        glVertex3f(+0.5, -0.5, +0.5)
        glVertex3f(+0.5, +0.5, +0.5)
        glVertex3f(-0.5, +0.5, +0.5)

        # back (-Z)
        glColor3f(0.0, 0.0, 1.0)
        glNormal3f(0.0, 0.0, -1.0)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, +0.5, -0.5)
        glVertex3f(+0.5, +0.5, -0.5)
        glVertex3f(+0.5, -0.5, -0.5)

        # left (-X)
        glColor3f(1.0, 0.0, 0.0)
        glNormal3f(-1.0, 0.0, 0.0)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, +0.5)
        glVertex3f(-0.5, +0.5, +0.5)
        glVertex3f(-0.5, +0.5, -0.5)

        # right (+X)
        glColor3f(1.0, 0.0, 0.0)
        glNormal3f(1.0, 0.0, 0.0)
        glVertex3f(+0.5, -0.5, -0.5)
        glVertex3f(+0.5, +0.5, -0.5)
        glVertex3f(+0.5, +0.5, +0.5)
        glVertex3f(+0.5, -0.5, +0.5)

        # top (+Y)
        glColor3f(0.0, 1.0, 0.0)
        glNormal3f(0.0, 1.0, 0.0)
        glVertex3f(-0.5, +0.5, -0.5)
        glVertex3f(-0.5, +0.5, +0.5)
        glVertex3f(+0.5, +0.5, +0.5)
        glVertex3f(+0.5, +0.5, -0.5)

        # bottom (-Y)

        glNormal3f(0.0, -1.0, 0.0)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(+0.5, -0.5, -0.5)
        glVertex3f(+0.5, -0.5, +0.5)
        glVertex3f(-0.5, -0.5, +0.5)

        glEnd()

    def draw_cylinder(self, inside: bool = False) -> None:
        glPushMatrix()
        glColor3f(1.0, 1.0, 0.0)
        quad = gluNewQuadric()
        gluQuadricOrientation(quad, GLU_INSIDE if inside else GLU_OUTSIDE)
        gluQuadricNormals(quad, GLU_FLAT)
        gluCylinder(quad, 0.5, 0.2, 1.0, 30, 10)
        gluDeleteQuadric(quad)
        glPopMatrix()

    def draw_light_marker(self) -> None:
        glPushMatrix()
        glPushAttrib(GL_LIGHTING_BIT)
        glDisable(GL_LIGHTING)
        glTranslatef(self.app_state.light_x, self.app_state.light_y, self.app_state.light_z)
        quad = gluNewQuadric()
        gluSphere(quad, 0.1, 10, 10)
        gluDeleteQuadric(quad)
        glPopAttrib()
        glPopMatrix()

    def keyPressEvent(self, ev: QtGui.QKeyEvent) -> None:
        key = ev.key()
        modifiers = ev.modifiers()
        txt = ev.text().lower()

        if txt:
            self._pressed_keys.add(txt)
        if txt == "?":
            self.app_state.show_help = not self.app_state.show_help
            print("Help:", "ON" if self.app_state.show_help else "OFF")

        if key == QtCore.Qt.Key.Key_Escape:
            QtWidgets.QApplication.quit()
        elif key == QtCore.Qt.Key.Key_Space:
            self.app_state.auto_rotate = not self.app_state.auto_rotate
            print("Auto-rotate:", "ON" if self.app_state.auto_rotate else "OFF")
        elif key == QtCore.Qt.Key.Key_1:
            self.app_state.lighting_enabled = not self.app_state.lighting_enabled
            print("Lighting:", "ON" if self.app_state.lighting_enabled else "OFF")
        elif key == QtCore.Qt.Key.Key_2:
            self.app_state.show_light_position = not self.app_state.show_light_position
            print("Light marker:", "ON" if self.app_state.show_light_position else "OFF")
        elif key == QtCore.Qt.Key.Key_3:
            self.app_state.depth_test = not self.app_state.depth_test
            print("Depth test:", "ON" if self.app_state.depth_test else "OFF")
        elif key == QtCore.Qt.Key.Key_4:
            modes = [GL_CONSTANT_ATTENUATION, GL_LINEAR_ATTENUATION, GL_QUADRATIC_ATTENUATION]
            idx = (
                modes.index(self.app_state.light_attenuation_mode)
                if self.app_state.light_attenuation_mode in modes
                else 0
            )
            idx = (idx + 1) % len(modes)
            self.app_state.light_attenuation_mode = modes[idx]
            label = {
                GL_CONSTANT_ATTENUATION: "constant",
                GL_LINEAR_ATTENUATION: "linear",
                GL_QUADRATIC_ATTENUATION: "quadratic",
            }[self.app_state.light_attenuation_mode]
            print("Attenuation:", label, "(", self.app_state.light_attenuation_value, ")")
        elif key == QtCore.Qt.Key.Key_5:
            if modifiers & QtCore.Qt.KeyboardModifier.ShiftModifier:
                self.app_state.light_attenuation_value = max(0.0, self.app_state.light_attenuation_value - 0.01)
            else:
                self.app_state.light_attenuation_value += 0.01
            print("Attenuation value:", self.app_state.light_attenuation_value)
        elif key == QtCore.Qt.Key.Key_6:
            self.app_state.light_model_local_viewer = not self.app_state.light_model_local_viewer
            print("Local viewer:", "ON" if self.app_state.light_model_local_viewer else "OFF")
        elif key == QtCore.Qt.Key.Key_7:
            self.app_state.light_model_two_side = not self.app_state.light_model_two_side
            print("Two-sided lighting:", "ON" if self.app_state.light_model_two_side else "OFF")
        elif key == QtCore.Qt.Key.Key_0:
            self.app_state.show_axis = not self.app_state.show_axis
            print("Axis:", "ON" if self.app_state.show_axis else "OFF")
        elif key == QtCore.Qt.Key.Key_O:
            self.app_state.camera_projection = Projection.ORTHOGONAL
            print("Projection: ortho")
            self.resizeGL(self.width(), self.height())
        elif key == QtCore.Qt.Key.Key_P:
            self.app_state.camera_projection = Projection.PERSPECTIVE
            print("Projection: perspective")
            self.resizeGL(self.width(), self.height())
        else:
            super().keyPressEvent(ev)

    def keyReleaseEvent(self, ev: QtGui.QKeyEvent) -> None:
        txt = ev.text().lower()
        if txt and txt in self._pressed_keys:
            self._pressed_keys.remove(txt)
        super().keyReleaseEvent(ev)

    def _tick(self) -> None:
        if "u" in self._pressed_keys:
            self.app_state.light_z -= 0.05
        if "j" in self._pressed_keys:
            self.app_state.light_z += 0.05
        if "h" in self._pressed_keys:
            self.app_state.light_x -= 0.05
        if "k" in self._pressed_keys:
            self.app_state.light_x += 0.05
        if "y" in self._pressed_keys:
            self.app_state.light_y += 0.05
        if "i" in self._pressed_keys:
            self.app_state.light_y -= 0.05

        if "q" in self._pressed_keys:
            if self.app_state.camera_projection == Projection.PERSPECTIVE:
                self.app_state.camera.distance += 0.02
            else:
                self.app_state.camera_ortho_half_height += 0.02
                self.resizeGL(self.width(), self.height())
        if "e" in self._pressed_keys:
            if self.app_state.camera_projection == Projection.PERSPECTIVE:
                self.app_state.camera.distance -= 0.02
            else:
                self.app_state.camera_ortho_half_height = max(0.01, self.app_state.camera_ortho_half_height - 0.02)
                self.resizeGL(self.width(), self.height())

        if "w" in self._pressed_keys:
            self.app_state.camera.theta += 0.02
        if "s" in self._pressed_keys:
            self.app_state.camera.theta -= 0.02
        if "a" in self._pressed_keys:
            self.app_state.camera.phi += 0.02
        if "d" in self._pressed_keys:
            self.app_state.camera.phi -= 0.02

        if "[" in self._pressed_keys:
            self.app_state.camera_perspective_fov = max(10.0, self.app_state.camera_perspective_fov - 0.2)
            if self.app_state.camera_projection == Projection.PERSPECTIVE:
                self.resizeGL(self.width(), self.height())
        if "]" in self._pressed_keys:
            self.app_state.camera_perspective_fov = min(120.0, self.app_state.camera_perspective_fov + 0.2)
            if self.app_state.camera_projection == Projection.PERSPECTIVE:
                self.resizeGL(self.width(), self.height())

        if "z" in self._pressed_keys:
            self.app_state.cube_distance += 0.02
        if "x" in self._pressed_keys:
            self.app_state.cube_distance -= 0.02

        self.update()
