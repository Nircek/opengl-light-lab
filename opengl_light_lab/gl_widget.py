import math
import time

from OpenGL.GL import (  # type: ignore
    GL_AMBIENT,
    GL_COLOR_BUFFER_BIT,
    GL_CONSTANT_ATTENUATION,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_DIFFUSE,
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
    GL_SMOOTH,
    GL_SPECULAR,
    GL_TEXTURE_2D,
    GLfloat,
    glBegin,
    glBindTexture,
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
    glMatrixMode,
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
from OpenGL.GLU import gluDeleteQuadric, gluLookAt, gluNewQuadric, gluPerspective, gluSphere  # type: ignore
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from opengl_light_lab import AppState, Projection, Spherical
from opengl_light_lab.app_state import LightType
from opengl_light_lab.input_handler import InputHandler
from opengl_light_lab.materials import (
    setup_material_blue,
    setup_material_green,
    setup_material_red,
    setup_material_white,
)
from opengl_light_lab.primitives import draw_cube, draw_cylinder, draw_quad, draw_textured_cube
from opengl_light_lab.textures import TextureManager

HELP_TEXT = """
Controls:
  Esc       - quit
  UHJKYI    - move light or direction (Z +/- / X +/- / Y +/-)
  QE        - zoom out/in (or change ortho half-height)
  WSAD      - change camera angles (theta / phi)
  []        - change FOV (perspective)
  ZX        - change cube distance
  ?         - toggle help overlay
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
        self._input_handler = InputHandler(app_state)
        self._texture_manager = TextureManager()

    def initializeGL(self) -> None:
        glClearColor(0.15, 0.15, 0.18, 1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glShadeModel(GL_SMOOTH)

        glEnable(GL_NORMALIZE)

        # Load texture if set
        self._texture_manager.load_if_changed(self.app_state.current_texture)

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

        # Check if texture needs to be loaded/updated
        self._texture_manager.load_if_changed(self.app_state.current_texture)

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
        setup_material_red()
        draw_cylinder(inside=True)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0.0, 0.0, 0.0)
        glRotatef(self.app_state.rotation_angle, 1, 0, 0)
        if self._texture_manager.is_loaded:
            setup_material_white()
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self._texture_manager.texture_id)
            draw_textured_cube()
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)
        else:
            setup_material_blue()
            draw_cube()
        glPopMatrix()

        glPushMatrix()
        glTranslatef(+self.app_state.cube_distance, 0.0, 0.0)
        glRotatef(self.app_state.rotation_angle, 0, 0, 1)
        setup_material_green()
        draw_cylinder(inside=False)
        glPopMatrix()

        if self.app_state.show_help:
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.RenderHint.TextAntialiasing)
            margin = 8
            w = min(300, self.width() - 20)
            h = min(200, self.height() - 20)
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
        if self.app_state.light_type == LightType.POINT:
            light_pos = (GLfloat * 4)(*self.app_state.light_position, 1.0)
        else:
            light_pos = (GLfloat * 4)(*self.app_state.light_direction, 0.0)

        light_diffuse = (GLfloat * 4)(*self.app_state.light_diffuse, 1.0)
        light_ambient = (GLfloat * 4)(*self.app_state.light_ambient, 1.0)
        light_specular = (GLfloat * 4)(*self.app_state.light_specular, 1.0)

        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

        # Attenuation: only for point light
        if self.app_state.light_type == LightType.POINT:
            glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.0)
            glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.0)
            glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.0)
            glLightf(GL_LIGHT0, self.app_state.light_attenuation_mode, self.app_state.light_attenuation_value)
        else:
            # No attenuation for directional
            glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
            glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.0)
            glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.0)

        glLightModelf(GL_LIGHT_MODEL_LOCAL_VIEWER, 1.0 if self.app_state.light_model_local_viewer else 0.0)
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, 1 if self.app_state.light_model_two_side else 0)

    def draw_light_marker(self) -> None:
        glPushAttrib(GL_LIGHTING_BIT)
        glDisable(GL_LIGHTING)
        if self.app_state.light_type == LightType.POINT:
            glPushMatrix()
            x, y, z = self.app_state.light_position
            glTranslatef(x, y, z)
            quad = gluNewQuadric()
            gluSphere(quad, 0.1, 10, 10)
            gluDeleteQuadric(quad)
            glPopMatrix()
        else:
            self._draw_directional_light_sun()
        glPopAttrib()

    def _draw_directional_light_sun(self) -> None:
        direction = self.app_state.light_direction
        length = math.sqrt(sum(d * d for d in direction))
        if length < 0.001:
            return

        sun_dist = self.app_state.camera.distance * 2.0
        sun_pos = tuple(d / length * sun_dist for d in direction)

        cam = self.app_state.camera
        to_cam = (cam.x - sun_pos[0], cam.y - sun_pos[1], cam.z - sun_pos[2])
        dist_to_cam = math.sqrt(sum(t * t for t in to_cam))
        yaw = math.atan2(to_cam[0], to_cam[2]) if dist_to_cam > 0.001 else 0.0
        pitch = math.asin(to_cam[1] / dist_to_cam) if dist_to_cam > 0.001 else 0.0

        glPushMatrix()
        glTranslatef(*sun_pos)
        glRotatef(yaw * 180.0 / math.pi, 0, 1, 0)
        glRotatef(-pitch * 180.0 / math.pi, 1, 0, 0)

        glColor3f(1.0, 1.0, 0.0)
        draw_quad(0.3)
        glPopMatrix()

    def keyPressEvent(self, ev: QtGui.QKeyEvent) -> None:
        key = ev.key()
        txt = ev.text().lower()

        if txt:
            self._input_handler.key_pressed(txt)
        if txt == "?":
            self.app_state.show_help = not self.app_state.show_help

        if key == QtCore.Qt.Key.Key_Escape:
            QtWidgets.QApplication.quit()
        else:
            super().keyPressEvent(ev)

    def keyReleaseEvent(self, ev: QtGui.QKeyEvent) -> None:
        txt = ev.text().lower()
        if txt:
            self._input_handler.key_released(txt)
        super().keyReleaseEvent(ev)

    def _tick(self) -> None:
        needs_resize = self._input_handler.update()
        if needs_resize:
            self.post_resize_event()
        self.update()

    def post_resize_event(self) -> None:
        app_instance = QtCore.QCoreApplication.instance()
        if app_instance is None:
            print("No QCoreApplication instance found")
            return
        app_instance.postEvent(self, QtGui.QResizeEvent(size := self.size(), size))
