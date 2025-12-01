from opengl_light_lab.app_state import AppState, LightType, Projection

LIGHT_MOVE_SPEED = 0.05
CAMERA_ROTATE_SPEED = 0.02
CAMERA_ZOOM_SPEED = 0.02
FOV_CHANGE_SPEED = 0.2
CUBE_DISTANCE_SPEED = 0.02


class InputHandler:
    """Handles keyboard input for the application.

    Tracks pressed keys and updates the application state based on input.
    """

    def __init__(self, app_state: AppState) -> None:
        """Initialize the input handler.

        Args:
            app_state: The shared application state object.
        """
        self.app_state = app_state
        self._pressed_keys: set[str] = set()

    def key_pressed(self, key: str) -> None:
        """Record a key as being pressed."""
        self._pressed_keys.add(key.lower())

    def key_released(self, key: str) -> None:
        """Record a key as being released."""
        key = key.lower()
        if key in self._pressed_keys:
            self._pressed_keys.discard(key)

    def is_pressed(self, key: str) -> bool:
        """Check if a key is currently pressed."""
        return key.lower() in self._pressed_keys

    def update(self) -> bool:
        """Process held keys and update app state.

        Returns:
            True if projection matrix needs to be updated.
        """
        needs_resize = False
        needs_resize |= self._handle_light_movement()
        needs_resize |= self._handle_camera_movement()
        needs_resize |= self._handle_object_movement()
        return needs_resize

    def _handle_light_movement(self) -> bool:
        """Handle light position/direction movement keys."""
        if self.app_state.light_type == LightType.POINT:
            x, y, z = self.app_state.light_position
            if self.is_pressed("u"):
                z -= LIGHT_MOVE_SPEED
            if self.is_pressed("j"):
                z += LIGHT_MOVE_SPEED
            if self.is_pressed("h"):
                x -= LIGHT_MOVE_SPEED
            if self.is_pressed("k"):
                x += LIGHT_MOVE_SPEED
            if self.is_pressed("y"):
                y += LIGHT_MOVE_SPEED
            if self.is_pressed("i"):
                y -= LIGHT_MOVE_SPEED
            self.app_state.light_position = (x, y, z)
        else:
            dx, dy, dz = self.app_state.light_direction
            if self.is_pressed("u"):
                dz -= LIGHT_MOVE_SPEED
            if self.is_pressed("j"):
                dz += LIGHT_MOVE_SPEED
            if self.is_pressed("h"):
                dx -= LIGHT_MOVE_SPEED
            if self.is_pressed("k"):
                dx += LIGHT_MOVE_SPEED
            if self.is_pressed("y"):
                dy += LIGHT_MOVE_SPEED
            if self.is_pressed("i"):
                dy -= LIGHT_MOVE_SPEED
            self.app_state.light_direction = (dx, dy, dz)
        return False

    def _handle_camera_movement(self) -> bool:
        """Handle camera movement and projection keys."""
        needs_resize = False

        # Zoom / ortho height
        if self.is_pressed("q"):
            if self.app_state.camera_projection == Projection.PERSPECTIVE:
                self.app_state.camera.distance += CAMERA_ZOOM_SPEED
            else:
                self.app_state.camera_ortho_half_height += CAMERA_ZOOM_SPEED
                needs_resize = True

        if self.is_pressed("e"):
            if self.app_state.camera_projection == Projection.PERSPECTIVE:
                self.app_state.camera.distance -= CAMERA_ZOOM_SPEED
            else:
                new_height = self.app_state.camera_ortho_half_height - CAMERA_ZOOM_SPEED
                self.app_state.camera_ortho_half_height = max(0.01, new_height)
                needs_resize = True

        # Camera rotation
        if self.is_pressed("w"):
            self.app_state.camera.theta += CAMERA_ROTATE_SPEED
        if self.is_pressed("s"):
            self.app_state.camera.theta -= CAMERA_ROTATE_SPEED
        if self.is_pressed("a"):
            self.app_state.camera.phi += CAMERA_ROTATE_SPEED
        if self.is_pressed("d"):
            self.app_state.camera.phi -= CAMERA_ROTATE_SPEED

        # FOV change
        if self.is_pressed("["):
            self.app_state.camera_perspective_fov = max(10.0, self.app_state.camera_perspective_fov - FOV_CHANGE_SPEED)
            if self.app_state.camera_projection == Projection.PERSPECTIVE:
                needs_resize = True

        if self.is_pressed("]"):
            self.app_state.camera_perspective_fov = min(120.0, self.app_state.camera_perspective_fov + FOV_CHANGE_SPEED)
            if self.app_state.camera_projection == Projection.PERSPECTIVE:
                needs_resize = True

        return needs_resize

    def _handle_object_movement(self) -> bool:
        """Handle object-related keys."""
        if self.is_pressed("z"):
            self.app_state.cube_distance += CUBE_DISTANCE_SPEED
        if self.is_pressed("x"):
            self.app_state.cube_distance -= CUBE_DISTANCE_SPEED
        return False
