from typing import TYPE_CHECKING, cast

from OpenGL.GL import GL_CONSTANT_ATTENUATION, GL_LINEAR_ATTENUATION, GL_QUADRATIC_ATTENUATION  # type: ignore
from PySide6 import QtCore, QtGui, QtWidgets

from opengl_light_lab import AppState, Projection
from opengl_light_lab.app_state import LightType

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

        # ===== Light Type Section =====
        light_type_group = QtWidgets.QGroupBox("Light Type")
        light_type_layout = QtWidgets.QHBoxLayout()

        self.light_type_combo = QtWidgets.QComboBox()
        self.light_type_combo.addItem("Point", LightType.POINT)
        self.light_type_combo.addItem("Directional", LightType.DIRECTIONAL)
        # Set current
        for i in range(self.light_type_combo.count()):
            if self.light_type_combo.itemData(i) == self.app_state.light_type:
                self.light_type_combo.setCurrentIndex(i)
                break
        self.light_type_combo.currentIndexChanged.connect(self._on_light_type_changed)
        light_type_layout.addWidget(self.light_type_combo)
        light_type_group.setLayout(light_type_layout)
        layout.addWidget(light_type_group)

        # ===== Light Position Section =====
        self.light_pos_group = QtWidgets.QGroupBox("Light Position (Point)")
        light_pos_layout = QtWidgets.QFormLayout()

        self.pos_x_spin = QtWidgets.QDoubleSpinBox()
        self.pos_x_spin.setRange(-10.0, 10.0)
        self.pos_x_spin.setSingleStep(0.1)
        self.pos_x_spin.setValue(self.app_state.light_position[0])
        self.pos_x_spin.valueChanged.connect(self._on_pos_x_changed)
        light_pos_layout.addRow("X:", self.pos_x_spin)

        self.pos_y_spin = QtWidgets.QDoubleSpinBox()
        self.pos_y_spin.setRange(-10.0, 10.0)
        self.pos_y_spin.setSingleStep(0.1)
        self.pos_y_spin.setValue(self.app_state.light_position[1])
        self.pos_y_spin.valueChanged.connect(self._on_pos_y_changed)
        light_pos_layout.addRow("Y:", self.pos_y_spin)

        self.pos_z_spin = QtWidgets.QDoubleSpinBox()
        self.pos_z_spin.setRange(-10.0, 10.0)
        self.pos_z_spin.setSingleStep(0.1)
        self.pos_z_spin.setValue(self.app_state.light_position[2])
        self.pos_z_spin.valueChanged.connect(self._on_pos_z_changed)
        light_pos_layout.addRow("Z:", self.pos_z_spin)

        self.light_pos_group.setLayout(light_pos_layout)
        layout.addWidget(self.light_pos_group)

        # ===== Light Direction Section =====
        self.light_dir_group = QtWidgets.QGroupBox("Light Direction (Directional)")
        light_layout = QtWidgets.QFormLayout()

        self.dir_x_spin = QtWidgets.QDoubleSpinBox()
        self.dir_x_spin.setRange(-10.0, 10.0)
        self.dir_x_spin.setSingleStep(0.1)
        self.dir_x_spin.setValue(self.app_state.light_direction[0])
        self.dir_x_spin.valueChanged.connect(self._on_dir_x_changed)
        light_layout.addRow("Dir X:", self.dir_x_spin)

        self.dir_y_spin = QtWidgets.QDoubleSpinBox()
        self.dir_y_spin.setRange(-10.0, 10.0)
        self.dir_y_spin.setSingleStep(0.1)
        self.dir_y_spin.setValue(self.app_state.light_direction[1])
        self.dir_y_spin.valueChanged.connect(self._on_dir_y_changed)
        light_layout.addRow("Dir Y:", self.dir_y_spin)

        self.dir_z_spin = QtWidgets.QDoubleSpinBox()
        self.dir_z_spin.setRange(-10.0, 10.0)
        self.dir_z_spin.setSingleStep(0.1)
        self.dir_z_spin.setValue(self.app_state.light_direction[2])
        self.dir_z_spin.valueChanged.connect(self._on_dir_z_changed)
        light_layout.addRow("Dir Z:", self.dir_z_spin)

        self.light_dir_group.setLayout(light_layout)
        layout.addWidget(self.light_dir_group)

        # ===== Light Attenuation Section =====
        self.light_atten_group = QtWidgets.QGroupBox("Light Attenuation (Point only)")
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

        self.light_atten_group.setLayout(light_atten_layout)
        layout.addWidget(self.light_atten_group)

        # ===== Light Colors Section =====
        self.light_colors_group = QtWidgets.QGroupBox("Light Colors")
        light_colors_layout = QtWidgets.QFormLayout()

        self.diffuse_btn = QtWidgets.QPushButton("Pick Diffuse")
        self.diffuse_btn.clicked.connect(self._pick_diffuse)
        self._update_color_button(self.diffuse_btn, self.app_state.light_diffuse)
        light_colors_layout.addRow("Diffuse:", self.diffuse_btn)

        self.ambient_btn = QtWidgets.QPushButton("Pick Ambient")
        self.ambient_btn.clicked.connect(self._pick_ambient)
        self._update_color_button(self.ambient_btn, self.app_state.light_ambient)
        light_colors_layout.addRow("Ambient:", self.ambient_btn)

        self.specular_btn = QtWidgets.QPushButton("Pick Specular")
        self.specular_btn.clicked.connect(self._pick_specular)
        self._update_color_button(self.specular_btn, self.app_state.light_specular)
        light_colors_layout.addRow("Specular:", self.specular_btn)

        self.light_colors_group.setLayout(light_colors_layout)
        layout.addWidget(self.light_colors_group)

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

        # Set up periodic sync timer
        self._sync_timer = QtCore.QTimer(self)
        self._sync_timer.timeout.connect(self._sync_from_app_state)
        self._sync_timer.start(500)  # 500ms = 0.5 seconds

        # Flag to prevent update loops
        self._updating_from_state = False

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

    # Position handlers
    def _on_pos_x_changed(self, value: float) -> None:
        _x, y, z = self.app_state.light_position
        self.app_state.light_position = (value, y, z)

    def _on_pos_y_changed(self, value: float) -> None:
        x, _y, z = self.app_state.light_position
        self.app_state.light_position = (x, value, z)

    def _on_pos_z_changed(self, value: float) -> None:
        x, y, _z = self.app_state.light_position
        self.app_state.light_position = (x, y, value)

    # Direction handlers
    def _on_dir_x_changed(self, value: float) -> None:
        _dx, dy, dz = self.app_state.light_direction
        self.app_state.light_direction = (value, dy, dz)

    def _on_dir_y_changed(self, value: float) -> None:
        dx, _dy, dz = self.app_state.light_direction
        self.app_state.light_direction = (dx, value, dz)

    def _on_dir_z_changed(self, value: float) -> None:
        dx, dy, _dz = self.app_state.light_direction
        self.app_state.light_direction = (dx, dy, value)

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

    # New light controls handlers
    def _on_light_type_changed(self, index: int) -> None:
        self.app_state.light_type = self.light_type_combo.itemData(index)
        # Update visibility/enabled status immediately
        is_point = self.app_state.light_type == LightType.POINT
        self.light_pos_group.setVisible(is_point)
        self.light_dir_group.setVisible(not is_point)
        self.light_atten_group.setEnabled(is_point)

    def _sync_from_app_state(self) -> None:
        """Synchronize UI controls with current app state.

        This method is called periodically to ensure the UI reflects any
        changes made to the app state from external sources. Uses signal
        blocking to prevent triggering change handlers during sync.
        """
        if self._updating_from_state:
            return

        self._updating_from_state = True
        try:
            # Light type visibility/enabled
            is_point = self.app_state.light_type == LightType.POINT
            if self.light_pos_group.isVisible() != is_point:
                self.light_pos_group.setVisible(is_point)
            if self.light_dir_group.isVisible() != (not is_point):
                self.light_dir_group.setVisible(not is_point)
            if self.light_atten_group.isEnabled() != is_point:
                self.light_atten_group.setEnabled(is_point)

            # Light type combo
            current_type = self.light_type_combo.currentData()
            if current_type != self.app_state.light_type:
                self.light_type_combo.blockSignals(True)
                for i in range(self.light_type_combo.count()):
                    if self.light_type_combo.itemData(i) == self.app_state.light_type:
                        self.light_type_combo.setCurrentIndex(i)
                        break
                self.light_type_combo.blockSignals(False)

            # Rendering checkboxes
            if self.lighting_cb.isChecked() != self.app_state.lighting_enabled:
                self.lighting_cb.blockSignals(True)
                self.lighting_cb.setChecked(self.app_state.lighting_enabled)
                self.lighting_cb.blockSignals(False)

            if self.depth_test_cb.isChecked() != self.app_state.depth_test:
                self.depth_test_cb.blockSignals(True)
                self.depth_test_cb.setChecked(self.app_state.depth_test)
                self.depth_test_cb.blockSignals(False)

            if self.show_axis_cb.isChecked() != self.app_state.show_axis:
                self.show_axis_cb.blockSignals(True)
                self.show_axis_cb.setChecked(self.app_state.show_axis)
                self.show_axis_cb.blockSignals(False)

            if self.show_light_cb.isChecked() != self.app_state.show_light_position:
                self.show_light_cb.blockSignals(True)
                self.show_light_cb.setChecked(self.app_state.show_light_position)
                self.show_light_cb.blockSignals(False)

            # Animation checkbox
            if self.auto_rotate_cb.isChecked() != self.app_state.auto_rotate:
                self.auto_rotate_cb.blockSignals(True)
                self.auto_rotate_cb.setChecked(self.app_state.auto_rotate)
                self.auto_rotate_cb.blockSignals(False)

            # Projection radio buttons
            is_perspective = self.app_state.camera_projection == Projection.PERSPECTIVE
            if self.proj_persp_rb.isChecked() != is_perspective:
                self.proj_persp_rb.blockSignals(True)
                self.proj_ortho_rb.blockSignals(True)
                self.proj_persp_rb.setChecked(is_perspective)
                self.proj_ortho_rb.setChecked(not is_perspective)
                self.proj_persp_rb.blockSignals(False)
                self.proj_ortho_rb.blockSignals(False)

            # Camera spinboxes
            if abs(self.camera_distance_spin.value() - self.app_state.camera.distance) > 1e-6:
                self.camera_distance_spin.blockSignals(True)
                self.camera_distance_spin.setValue(self.app_state.camera.distance)
                self.camera_distance_spin.blockSignals(False)

            if abs(self.camera_theta_spin.value() - self.app_state.camera.theta) > 1e-6:
                self.camera_theta_spin.blockSignals(True)
                self.camera_theta_spin.setValue(self.app_state.camera.theta)
                self.camera_theta_spin.blockSignals(False)

            if abs(self.camera_phi_spin.value() - self.app_state.camera.phi) > 1e-6:
                self.camera_phi_spin.blockSignals(True)
                self.camera_phi_spin.setValue(self.app_state.camera.phi)
                self.camera_phi_spin.blockSignals(False)

            if abs(self.fov_spin.value() - self.app_state.camera_perspective_fov) > 1e-6:
                self.fov_spin.blockSignals(True)
                self.fov_spin.setValue(self.app_state.camera_perspective_fov)
                self.fov_spin.blockSignals(False)

            if abs(self.ortho_height_spin.value() - self.app_state.camera_ortho_half_height) > 1e-6:
                self.ortho_height_spin.blockSignals(True)
                self.ortho_height_spin.setValue(self.app_state.camera_ortho_half_height)
                self.ortho_height_spin.blockSignals(False)

            # Light position spinboxes
            px, py, pz = self.app_state.light_position
            if abs(self.pos_x_spin.value() - px) > 1e-6:
                self.pos_x_spin.blockSignals(True)
                self.pos_x_spin.setValue(px)
                self.pos_x_spin.blockSignals(False)
            if abs(self.pos_y_spin.value() - py) > 1e-6:
                self.pos_y_spin.blockSignals(True)
                self.pos_y_spin.setValue(py)
                self.pos_y_spin.blockSignals(False)
            if abs(self.pos_z_spin.value() - pz) > 1e-6:
                self.pos_z_spin.blockSignals(True)
                self.pos_z_spin.setValue(pz)
                self.pos_z_spin.blockSignals(False)

            # Light direction spinboxes
            dx, dy, dz = self.app_state.light_direction
            if abs(self.dir_x_spin.value() - dx) > 1e-6:
                self.dir_x_spin.blockSignals(True)
                self.dir_x_spin.setValue(dx)
                self.dir_x_spin.blockSignals(False)
            if abs(self.dir_y_spin.value() - dy) > 1e-6:
                self.dir_y_spin.blockSignals(True)
                self.dir_y_spin.setValue(dy)
                self.dir_y_spin.blockSignals(False)
            if abs(self.dir_z_spin.value() - dz) > 1e-6:
                self.dir_z_spin.blockSignals(True)
                self.dir_z_spin.setValue(dz)
                self.dir_z_spin.blockSignals(False)

            # Attenuation combo box
            current_mode = self.atten_mode_combo.currentData()
            if current_mode != self.app_state.light_attenuation_mode:
                self.atten_mode_combo.blockSignals(True)
                for i in range(self.atten_mode_combo.count()):
                    if self.atten_mode_combo.itemData(i) == self.app_state.light_attenuation_mode:
                        self.atten_mode_combo.setCurrentIndex(i)
                        break
                self.atten_mode_combo.blockSignals(False)

            if abs(self.atten_value_spin.value() - self.app_state.light_attenuation_value) > 1e-6:
                self.atten_value_spin.blockSignals(True)
                self.atten_value_spin.setValue(self.app_state.light_attenuation_value)
                self.atten_value_spin.blockSignals(False)

            # Light colors buttons preview
            self._update_color_button(self.diffuse_btn, self.app_state.light_diffuse)
            self._update_color_button(self.ambient_btn, self.app_state.light_ambient)
            self._update_color_button(self.specular_btn, self.app_state.light_specular)

            # Light model checkboxes
            if self.local_viewer_cb.isChecked() != self.app_state.light_model_local_viewer:
                self.local_viewer_cb.blockSignals(True)
                self.local_viewer_cb.setChecked(self.app_state.light_model_local_viewer)
                self.local_viewer_cb.blockSignals(False)

            if self.two_side_cb.isChecked() != self.app_state.light_model_two_side:
                self.two_side_cb.blockSignals(True)
                self.two_side_cb.setChecked(self.app_state.light_model_two_side)
                self.two_side_cb.blockSignals(False)

            # Object spinbox
            if abs(self.cube_distance_spin.value() - self.app_state.cube_distance) > 1e-6:
                self.cube_distance_spin.blockSignals(True)
                self.cube_distance_spin.setValue(self.app_state.cube_distance)
                self.cube_distance_spin.blockSignals(False)

        finally:
            self._updating_from_state = False

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Clean up resources when the widget is closed."""
        self._sync_timer.stop()
        super().closeEvent(event)

    # Color pickers helpers
    def _pick_color(self, initial: tuple[float, float, float]) -> tuple[float, float, float] | None:
        r, g, b = [int(255 * max(0.0, min(1.0, c))) for c in initial]
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(r, g, b), self, "Select Color")
        if color.isValid():
            return (color.redF(), color.greenF(), color.blueF())
        return None

    def _update_color_button(self, btn: QtWidgets.QPushButton, rgb: tuple[float, float, float]) -> None:
        r, g, b = [int(255 * max(0.0, min(1.0, c))) for c in rgb]
        btn.setStyleSheet(f"background-color: rgb({r}, {g}, {b});")

    def _pick_diffuse(self) -> None:
        res = self._pick_color(self.app_state.light_diffuse)
        if res is not None:
            self.app_state.light_diffuse = res
            self._update_color_button(self.diffuse_btn, res)

    def _pick_ambient(self) -> None:
        res = self._pick_color(self.app_state.light_ambient)
        if res is not None:
            self.app_state.light_ambient = res
            self._update_color_button(self.ambient_btn, res)

    def _pick_specular(self) -> None:
        res = self._pick_color(self.app_state.light_specular)
        if res is not None:
            self.app_state.light_specular = res
            self._update_color_button(self.specular_btn, res)
