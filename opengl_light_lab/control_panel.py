from typing import TYPE_CHECKING, cast

from OpenGL.GL import GL_CONSTANT_ATTENUATION, GL_LINEAR_ATTENUATION, GL_QUADRATIC_ATTENUATION  # type: ignore
from PySide6 import QtWidgets

from opengl_light_lab import AppState, Projection

if TYPE_CHECKING:
    from opengl_light_lab.main_window import MainWindow


class ControlPanel(QtWidgets.QDockWidget):
    def __init__(self, parent: QtWidgets.QWidget | None, app_state: AppState) -> None:  # noqa: PLR0914
        super().__init__("Controls", parent)
        self.app_state = app_state

        # Make the dock widget non-closable but allow floating
        self.setFeatures(
            QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable
        )

        # Create the main widget and layout
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(main_widget)

        # Create scroll area for all controls
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(scroll_content)

        # ===== Rendering Section =====
        rendering_group = QtWidgets.QGroupBox("Rendering")
        rendering_layout = QtWidgets.QVBoxLayout()

        self.lighting_cb = QtWidgets.QCheckBox("Enable Lighting")
        self.lighting_cb.setChecked(self.app_state.lighting_enabled)
        self.lighting_cb.stateChanged.connect(self._on_lighting_changed)
        rendering_layout.addWidget(self.lighting_cb)

        self.depth_test_cb = QtWidgets.QCheckBox("Enable Depth Test")
        self.depth_test_cb.setChecked(self.app_state.depth_test)
        self.depth_test_cb.stateChanged.connect(self._on_depth_test_changed)
        rendering_layout.addWidget(self.depth_test_cb)

        self.show_axis_cb = QtWidgets.QCheckBox("Show Axis")
        self.show_axis_cb.setChecked(self.app_state.show_axis)
        self.show_axis_cb.stateChanged.connect(self._on_show_axis_changed)
        rendering_layout.addWidget(self.show_axis_cb)

        self.show_light_cb = QtWidgets.QCheckBox("Show Light Marker")
        self.show_light_cb.setChecked(self.app_state.show_light_position)
        self.show_light_cb.stateChanged.connect(self._on_show_light_changed)
        rendering_layout.addWidget(self.show_light_cb)

        rendering_group.setLayout(rendering_layout)
        layout.addWidget(rendering_group)

        # ===== Animation Section =====
        animation_group = QtWidgets.QGroupBox("Animation")
        animation_layout = QtWidgets.QVBoxLayout()

        self.auto_rotate_cb = QtWidgets.QCheckBox("Auto-Rotate")
        self.auto_rotate_cb.setChecked(self.app_state.auto_rotate)
        self.auto_rotate_cb.stateChanged.connect(self._on_auto_rotate_changed)
        animation_layout.addWidget(self.auto_rotate_cb)

        animation_group.setLayout(animation_layout)
        layout.addWidget(animation_group)

        # ===== Camera Section =====
        camera_group = QtWidgets.QGroupBox("Camera")
        camera_layout = QtWidgets.QFormLayout()

        # Projection type
        proj_layout = QtWidgets.QHBoxLayout()
        self.proj_persp_rb = QtWidgets.QRadioButton("Perspective")
        self.proj_ortho_rb = QtWidgets.QRadioButton("Orthogonal")
        if self.app_state.camera_projection == Projection.PERSPECTIVE:
            self.proj_persp_rb.setChecked(True)
        else:
            self.proj_ortho_rb.setChecked(True)
        self.proj_persp_rb.toggled.connect(self._on_projection_changed)
        proj_layout.addWidget(self.proj_persp_rb)
        proj_layout.addWidget(self.proj_ortho_rb)
        camera_layout.addRow("Projection:", proj_layout)

        # Camera distance
        self.camera_distance_spin = QtWidgets.QDoubleSpinBox()
        self.camera_distance_spin.setRange(0.1, 50.0)
        self.camera_distance_spin.setSingleStep(0.1)
        self.camera_distance_spin.setValue(self.app_state.camera.distance)
        self.camera_distance_spin.valueChanged.connect(self._on_camera_distance_changed)
        camera_layout.addRow("Distance:", self.camera_distance_spin)

        # Camera theta
        self.camera_theta_spin = QtWidgets.QDoubleSpinBox()
        self.camera_theta_spin.setRange(-10.0, 10.0)
        self.camera_theta_spin.setSingleStep(0.1)
        self.camera_theta_spin.setValue(self.app_state.camera.theta)
        self.camera_theta_spin.valueChanged.connect(self._on_camera_theta_changed)
        camera_layout.addRow("Theta:", self.camera_theta_spin)

        # Camera phi
        self.camera_phi_spin = QtWidgets.QDoubleSpinBox()
        self.camera_phi_spin.setRange(-10.0, 10.0)
        self.camera_phi_spin.setSingleStep(0.1)
        self.camera_phi_spin.setValue(self.app_state.camera.phi)
        self.camera_phi_spin.valueChanged.connect(self._on_camera_phi_changed)
        camera_layout.addRow("Phi:", self.camera_phi_spin)

        # Perspective FOV
        self.fov_spin = QtWidgets.QDoubleSpinBox()
        self.fov_spin.setRange(10.0, 120.0)
        self.fov_spin.setSingleStep(1.0)
        self.fov_spin.setValue(self.app_state.camera_perspective_fov)
        self.fov_spin.valueChanged.connect(self._on_fov_changed)
        camera_layout.addRow("FOV (Perspective):", self.fov_spin)

        # Ortho half height
        self.ortho_height_spin = QtWidgets.QDoubleSpinBox()
        self.ortho_height_spin.setRange(0.01, 10.0)
        self.ortho_height_spin.setSingleStep(0.1)
        self.ortho_height_spin.setValue(self.app_state.camera_ortho_half_height)
        self.ortho_height_spin.valueChanged.connect(self._on_ortho_height_changed)
        camera_layout.addRow("Ortho Half Height:", self.ortho_height_spin)

        camera_group.setLayout(camera_layout)
        layout.addWidget(camera_group)

        # ===== Light Position Section =====
        light_pos_group = QtWidgets.QGroupBox("Light Position")
        light_pos_layout = QtWidgets.QFormLayout()

        self.light_x_spin = QtWidgets.QDoubleSpinBox()
        self.light_x_spin.setRange(-10.0, 10.0)
        self.light_x_spin.setSingleStep(0.1)
        self.light_x_spin.setValue(self.app_state.light_x)
        self.light_x_spin.valueChanged.connect(self._on_light_x_changed)
        light_pos_layout.addRow("X:", self.light_x_spin)

        self.light_y_spin = QtWidgets.QDoubleSpinBox()
        self.light_y_spin.setRange(-10.0, 10.0)
        self.light_y_spin.setSingleStep(0.1)
        self.light_y_spin.setValue(self.app_state.light_y)
        self.light_y_spin.valueChanged.connect(self._on_light_y_changed)
        light_pos_layout.addRow("Y:", self.light_y_spin)

        self.light_z_spin = QtWidgets.QDoubleSpinBox()
        self.light_z_spin.setRange(-10.0, 10.0)
        self.light_z_spin.setSingleStep(0.1)
        self.light_z_spin.setValue(self.app_state.light_z)
        self.light_z_spin.valueChanged.connect(self._on_light_z_changed)
        light_pos_layout.addRow("Z:", self.light_z_spin)

        light_pos_group.setLayout(light_pos_layout)
        layout.addWidget(light_pos_group)

        # ===== Light Attenuation Section =====
        light_atten_group = QtWidgets.QGroupBox("Light Attenuation")
        light_atten_layout = QtWidgets.QFormLayout()

        self.atten_mode_combo = QtWidgets.QComboBox()
        self.atten_mode_combo.addItem("Constant", GL_CONSTANT_ATTENUATION)
        self.atten_mode_combo.addItem("Linear", GL_LINEAR_ATTENUATION)
        self.atten_mode_combo.addItem("Quadratic", GL_QUADRATIC_ATTENUATION)
        # Set current mode
        for i in range(self.atten_mode_combo.count()):
            if self.atten_mode_combo.itemData(i) == self.app_state.light_attenuation_mode:
                self.atten_mode_combo.setCurrentIndex(i)
                break
        self.atten_mode_combo.currentIndexChanged.connect(self._on_attenuation_mode_changed)
        light_atten_layout.addRow("Mode:", self.atten_mode_combo)

        self.atten_value_spin = QtWidgets.QDoubleSpinBox()
        self.atten_value_spin.setRange(0.0, 10.0)
        self.atten_value_spin.setSingleStep(0.01)
        self.atten_value_spin.setDecimals(3)
        self.atten_value_spin.setValue(self.app_state.light_attenuation_value)
        self.atten_value_spin.valueChanged.connect(self._on_attenuation_value_changed)
        light_atten_layout.addRow("Value:", self.atten_value_spin)

        light_atten_group.setLayout(light_atten_layout)
        layout.addWidget(light_atten_group)

        # ===== Light Model Section =====
        light_model_group = QtWidgets.QGroupBox("Light Model")
        light_model_layout = QtWidgets.QVBoxLayout()

        self.local_viewer_cb = QtWidgets.QCheckBox("Local Viewer")
        self.local_viewer_cb.setChecked(self.app_state.light_model_local_viewer)
        self.local_viewer_cb.stateChanged.connect(self._on_local_viewer_changed)
        light_model_layout.addWidget(self.local_viewer_cb)

        self.two_side_cb = QtWidgets.QCheckBox("Two-Sided Lighting")
        self.two_side_cb.setChecked(self.app_state.light_model_two_side)
        self.two_side_cb.stateChanged.connect(self._on_two_side_changed)
        light_model_layout.addWidget(self.two_side_cb)

        light_model_group.setLayout(light_model_layout)
        layout.addWidget(light_model_group)

        # ===== Object Section =====
        object_group = QtWidgets.QGroupBox("Object")
        object_layout = QtWidgets.QFormLayout()

        self.cube_distance_spin = QtWidgets.QDoubleSpinBox()
        self.cube_distance_spin.setRange(0.0, 10.0)
        self.cube_distance_spin.setSingleStep(0.1)
        self.cube_distance_spin.setValue(self.app_state.cube_distance)
        self.cube_distance_spin.valueChanged.connect(self._on_cube_distance_changed)
        object_layout.addRow("Cube Distance:", self.cube_distance_spin)

        object_group.setLayout(object_layout)
        layout.addWidget(object_group)

        # Add stretch to push everything to the top
        layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        self.setWidget(main_widget)

    def _on_lighting_changed(self, state: int) -> None:
        self.app_state.lighting_enabled = bool(state)

    def _on_depth_test_changed(self, state: int) -> None:
        self.app_state.depth_test = bool(state)

    def _on_show_axis_changed(self, state: int) -> None:
        self.app_state.show_axis = bool(state)

    def _on_show_light_changed(self, state: int) -> None:
        self.app_state.show_light_position = bool(state)

    def _on_auto_rotate_changed(self, state: int) -> None:
        self.app_state.auto_rotate = bool(state)

    def _on_projection_changed(self, checked: bool) -> None:
        if checked:
            self.app_state.camera_projection = Projection.PERSPECTIVE
        else:
            self.app_state.camera_projection = Projection.ORTHOGONAL
        # Notify parent to resize GL viewport
        if self.parent():
            self.parent().on_projection_changed()  # type: ignore

    def _on_camera_distance_changed(self, value: float) -> None:
        self.app_state.camera.distance = value

    def _on_camera_theta_changed(self, value: float) -> None:
        self.app_state.camera.theta = value

    def _on_camera_phi_changed(self, value: float) -> None:
        self.app_state.camera.phi = value

    def _on_fov_changed(self, value: float) -> None:
        self.app_state.camera_perspective_fov = value
        if self.app_state.camera_projection == Projection.PERSPECTIVE and self.parent():
            cast("MainWindow", self.parent()).on_projection_changed()

    def _on_ortho_height_changed(self, value: float) -> None:
        self.app_state.camera_ortho_half_height = value
        if self.app_state.camera_projection == Projection.ORTHOGONAL and self.parent():
            cast("MainWindow", self.parent()).on_projection_changed()

    def _on_light_x_changed(self, value: float) -> None:
        self.app_state.light_x = value

    def _on_light_y_changed(self, value: float) -> None:
        self.app_state.light_y = value

    def _on_light_z_changed(self, value: float) -> None:
        self.app_state.light_z = value

    def _on_attenuation_mode_changed(self, index: int) -> None:
        self.app_state.light_attenuation_mode = self.atten_mode_combo.itemData(index)

    def _on_attenuation_value_changed(self, value: float) -> None:
        self.app_state.light_attenuation_value = value

    def _on_local_viewer_changed(self, state: int) -> None:
        self.app_state.light_model_local_viewer = bool(state)

    def _on_two_side_changed(self, state: int) -> None:
        self.app_state.light_model_two_side = bool(state)

    def _on_cube_distance_changed(self, value: float) -> None:
        self.app_state.cube_distance = value
