from pathlib import Path
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

        # ===== Scene Section =====
        scene_group = QtWidgets.QGroupBox("Scene")
        scene_layout = QtWidgets.QVBoxLayout()

        self.auto_rotate_cb = QtWidgets.QCheckBox("Auto-Rotate Objects")
        self.auto_rotate_cb.setChecked(self.app_state.auto_rotate)
        self.auto_rotate_cb.stateChanged.connect(self._on_auto_rotate_changed)
        scene_layout.addWidget(self.auto_rotate_cb)

        self.show_axis_cb = QtWidgets.QCheckBox("Show Coordinate Axes")
        self.show_axis_cb.setChecked(self.app_state.show_axis)
        self.show_axis_cb.stateChanged.connect(self._on_show_axis_changed)
        scene_layout.addWidget(self.show_axis_cb)

        self.show_light_cb = QtWidgets.QCheckBox("Show Light Marker")
        self.show_light_cb.setChecked(self.app_state.show_light_position)
        self.show_light_cb.stateChanged.connect(self._on_show_light_changed)
        scene_layout.addWidget(self.show_light_cb)

        self.lighting_cb = QtWidgets.QCheckBox("Enable Lighting")
        self.lighting_cb.setChecked(self.app_state.lighting_enabled)
        self.lighting_cb.stateChanged.connect(self._on_lighting_changed)
        scene_layout.addWidget(self.lighting_cb)

        self.depth_test_cb = QtWidgets.QCheckBox("Enable Depth Test")
        self.depth_test_cb.setChecked(self.app_state.depth_test)
        self.depth_test_cb.stateChanged.connect(self._on_depth_test_changed)
        scene_layout.addWidget(self.depth_test_cb)

        scene_group.setLayout(scene_layout)
        layout.addWidget(scene_group)

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

        # ===== Light Source Section =====
        light_source_group = QtWidgets.QGroupBox("Light Source")
        light_source_layout = QtWidgets.QFormLayout()

        # Light type combo
        self.light_type_combo = QtWidgets.QComboBox()
        self.light_type_combo.addItem("Point Light", LightType.POINT)
        self.light_type_combo.addItem("Directional Light", LightType.DIRECTIONAL)
        for i in range(self.light_type_combo.count()):
            if self.light_type_combo.itemData(i) == self.app_state.light_type:
                self.light_type_combo.setCurrentIndex(i)
                break
        self.light_type_combo.currentIndexChanged.connect(self._on_light_type_changed)
        light_source_layout.addRow("Type:", self.light_type_combo)

        # Position controls (for point light)
        self._pos_label = QtWidgets.QLabel("Position:")
        self.pos_x_spin = QtWidgets.QDoubleSpinBox()
        self.pos_x_spin.setRange(-10.0, 10.0)
        self.pos_x_spin.setSingleStep(0.1)
        self.pos_x_spin.setValue(self.app_state.light_position[0])
        self.pos_x_spin.valueChanged.connect(self._on_pos_x_changed)

        self.pos_y_spin = QtWidgets.QDoubleSpinBox()
        self.pos_y_spin.setRange(-10.0, 10.0)
        self.pos_y_spin.setSingleStep(0.1)
        self.pos_y_spin.setValue(self.app_state.light_position[1])
        self.pos_y_spin.valueChanged.connect(self._on_pos_y_changed)

        self.pos_z_spin = QtWidgets.QDoubleSpinBox()
        self.pos_z_spin.setRange(-10.0, 10.0)
        self.pos_z_spin.setSingleStep(0.1)
        self.pos_z_spin.setValue(self.app_state.light_position[2])
        self.pos_z_spin.valueChanged.connect(self._on_pos_z_changed)

        pos_widget = QtWidgets.QWidget()
        pos_layout = QtWidgets.QHBoxLayout(pos_widget)
        pos_layout.setContentsMargins(0, 0, 0, 0)
        pos_layout.addWidget(QtWidgets.QLabel("X:"))
        pos_layout.addWidget(self.pos_x_spin)
        pos_layout.addWidget(QtWidgets.QLabel("Y:"))
        pos_layout.addWidget(self.pos_y_spin)
        pos_layout.addWidget(QtWidgets.QLabel("Z:"))
        pos_layout.addWidget(self.pos_z_spin)
        light_source_layout.addRow(self._pos_label, pos_widget)

        # Direction controls (for directional light)
        self._dir_label = QtWidgets.QLabel("Direction:")
        self.dir_x_spin = QtWidgets.QDoubleSpinBox()
        self.dir_x_spin.setRange(-10.0, 10.0)
        self.dir_x_spin.setSingleStep(0.1)
        self.dir_x_spin.setValue(self.app_state.light_direction[0])
        self.dir_x_spin.valueChanged.connect(self._on_dir_x_changed)

        self.dir_y_spin = QtWidgets.QDoubleSpinBox()
        self.dir_y_spin.setRange(-10.0, 10.0)
        self.dir_y_spin.setSingleStep(0.1)
        self.dir_y_spin.setValue(self.app_state.light_direction[1])
        self.dir_y_spin.valueChanged.connect(self._on_dir_y_changed)

        self.dir_z_spin = QtWidgets.QDoubleSpinBox()
        self.dir_z_spin.setRange(-10.0, 10.0)
        self.dir_z_spin.setSingleStep(0.1)
        self.dir_z_spin.setValue(self.app_state.light_direction[2])
        self.dir_z_spin.valueChanged.connect(self._on_dir_z_changed)

        dir_widget = QtWidgets.QWidget()
        dir_layout = QtWidgets.QHBoxLayout(dir_widget)
        dir_layout.setContentsMargins(0, 0, 0, 0)
        dir_layout.addWidget(QtWidgets.QLabel("X:"))
        dir_layout.addWidget(self.dir_x_spin)
        dir_layout.addWidget(QtWidgets.QLabel("Y:"))
        dir_layout.addWidget(self.dir_y_spin)
        dir_layout.addWidget(QtWidgets.QLabel("Z:"))
        dir_layout.addWidget(self.dir_z_spin)
        light_source_layout.addRow(self._dir_label, dir_widget)
        self._dir_widget = dir_widget
        self._pos_widget = pos_widget

        # Attenuation (point light only)
        self._atten_label = QtWidgets.QLabel("Attenuation:")
        self.atten_mode_combo = QtWidgets.QComboBox()
        self.atten_mode_combo.addItem("Constant", GL_CONSTANT_ATTENUATION)
        self.atten_mode_combo.addItem("Linear", GL_LINEAR_ATTENUATION)
        self.atten_mode_combo.addItem("Quadratic", GL_QUADRATIC_ATTENUATION)
        for i in range(self.atten_mode_combo.count()):
            if self.atten_mode_combo.itemData(i) == self.app_state.light_attenuation_mode:
                self.atten_mode_combo.setCurrentIndex(i)
                break
        self.atten_mode_combo.currentIndexChanged.connect(self._on_attenuation_mode_changed)

        self.atten_value_spin = QtWidgets.QDoubleSpinBox()
        self.atten_value_spin.setRange(0.0, 10.0)
        self.atten_value_spin.setSingleStep(0.01)
        self.atten_value_spin.setDecimals(3)
        self.atten_value_spin.setValue(self.app_state.light_attenuation_value)
        self.atten_value_spin.valueChanged.connect(self._on_attenuation_value_changed)

        atten_widget = QtWidgets.QWidget()
        atten_layout = QtWidgets.QHBoxLayout(atten_widget)
        atten_layout.setContentsMargins(0, 0, 0, 0)
        atten_layout.addWidget(self.atten_mode_combo)
        atten_layout.addWidget(QtWidgets.QLabel("Value:"))
        atten_layout.addWidget(self.atten_value_spin)
        light_source_layout.addRow(self._atten_label, atten_widget)
        self._atten_widget = atten_widget

        light_source_group.setLayout(light_source_layout)
        layout.addWidget(light_source_group)

        # ===== Light Properties Section =====
        light_props_group = QtWidgets.QGroupBox("Light Properties")
        light_props_layout = QtWidgets.QFormLayout()

        self.diffuse_btn = QtWidgets.QPushButton("Pick")
        self.diffuse_btn.clicked.connect(self._pick_diffuse)
        self._update_color_button(self.diffuse_btn, self.app_state.light_diffuse)
        light_props_layout.addRow("Diffuse Color:", self.diffuse_btn)

        self.ambient_btn = QtWidgets.QPushButton("Pick")
        self.ambient_btn.clicked.connect(self._pick_ambient)
        self._update_color_button(self.ambient_btn, self.app_state.light_ambient)
        light_props_layout.addRow("Ambient Color:", self.ambient_btn)

        self.specular_btn = QtWidgets.QPushButton("Pick")
        self.specular_btn.clicked.connect(self._pick_specular)
        self._update_color_button(self.specular_btn, self.app_state.light_specular)
        light_props_layout.addRow("Specular Color:", self.specular_btn)

        self.local_viewer_cb = QtWidgets.QCheckBox("Local Viewer")
        self.local_viewer_cb.setChecked(self.app_state.light_model_local_viewer)
        self.local_viewer_cb.stateChanged.connect(self._on_local_viewer_changed)
        light_props_layout.addRow("", self.local_viewer_cb)

        self.two_side_cb = QtWidgets.QCheckBox("Two-Sided Lighting")
        self.two_side_cb.setChecked(self.app_state.light_model_two_side)
        self.two_side_cb.stateChanged.connect(self._on_two_side_changed)
        light_props_layout.addRow("", self.two_side_cb)

        light_props_group.setLayout(light_props_layout)
        layout.addWidget(light_props_group)

        # ===== Objects Section =====
        objects_group = QtWidgets.QGroupBox("Objects")
        objects_layout = QtWidgets.QFormLayout()

        self.cube_distance_spin = QtWidgets.QDoubleSpinBox()
        self.cube_distance_spin.setRange(0.0, 10.0)
        self.cube_distance_spin.setSingleStep(0.1)
        self.cube_distance_spin.setValue(self.app_state.cube_distance)
        self.cube_distance_spin.valueChanged.connect(self._on_cube_distance_changed)
        objects_layout.addRow("Side Objects Distance:", self.cube_distance_spin)

        self.texture_combo = QtWidgets.QComboBox()
        self._texture_files: dict[str, str] = {}  # display name -> full path
        self._populate_texture_combo()
        self.texture_combo.currentIndexChanged.connect(self._on_texture_changed)
        objects_layout.addRow("Center Cube Texture:", self.texture_combo)

        objects_group.setLayout(objects_layout)
        layout.addWidget(objects_group)

        # Initial visibility based on light type
        is_point = self.app_state.light_type == LightType.POINT
        self._pos_label.setVisible(is_point)
        self._pos_widget.setVisible(is_point)
        self._dir_label.setVisible(not is_point)
        self._dir_widget.setVisible(not is_point)
        self._atten_label.setVisible(is_point)
        self._atten_widget.setVisible(is_point)

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

    def _populate_texture_combo(self) -> None:
        """Scan textures folder and populate the combo box."""
        self.texture_combo.clear()
        self._texture_files.clear()

        # Add "None" option
        self.texture_combo.addItem("(None)")
        self._texture_files["(None)"] = ""

        # Find textures folder relative to this module
        textures_dir = Path(__file__).parent.parent / "textures"
        if not textures_dir.exists():
            return

        # Scan for jpg/jpeg files
        jpg_files = list(textures_dir.glob("*.jpg")) + list(textures_dir.glob("*.jpeg"))
        jpg_files.sort()

        current_index = 0
        for i, jpg_path in enumerate(jpg_files, start=1):
            # Extract display name (part before underscore)
            filename = jpg_path.stem  # filename without extension
            display_name = filename.split("_")[0] if "_" in filename else filename

            self.texture_combo.addItem(display_name)
            self._texture_files[display_name] = str(jpg_path)

            # Check if this is the currently selected texture
            if self.app_state.current_texture == str(jpg_path):
                current_index = i

        self.texture_combo.setCurrentIndex(current_index)

    def _on_texture_changed(self, _index: int) -> None:
        """Handle texture selection change."""
        display_name = self.texture_combo.currentText()
        texture_path = self._texture_files.get(display_name, "")
        self.app_state.current_texture = texture_path or None

    # New light controls handlers
    def _on_light_type_changed(self, index: int) -> None:
        self.app_state.light_type = self.light_type_combo.itemData(index)
        # Update visibility/enabled status immediately
        is_point = self.app_state.light_type == LightType.POINT
        self._pos_label.setVisible(is_point)
        self._pos_widget.setVisible(is_point)
        self._dir_label.setVisible(not is_point)
        self._dir_widget.setVisible(not is_point)
        self._atten_label.setVisible(is_point)
        self._atten_widget.setVisible(is_point)

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
            if self._pos_widget.isVisible() != is_point:
                self._pos_label.setVisible(is_point)
                self._pos_widget.setVisible(is_point)
            if self._dir_widget.isVisible() != (not is_point):
                self._dir_label.setVisible(not is_point)
                self._dir_widget.setVisible(not is_point)
            if self._atten_widget.isVisible() != is_point:
                self._atten_label.setVisible(is_point)
                self._atten_widget.setVisible(is_point)

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
