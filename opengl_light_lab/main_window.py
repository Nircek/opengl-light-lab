from PySide6 import QtCore, QtWidgets

from opengl_light_lab import AppState, ControlPanel, GLWidget


class MainWindow(QtWidgets.QMainWindow):
    """Main application window.

    Hosts the GLWidget and ControlPanel.
    """

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()
        self.setWindowTitle("OpenGL Light Lab")
        self.app_state = AppState()
        self.gl = GLWidget(self, self.app_state)
        self.gl.makeCurrent()
        self.setCentralWidget(self.gl)

        self.control_panel = ControlPanel(self, self.app_state)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.control_panel)

        self.resize(1280, 768)

    def on_projection_changed(self) -> None:
        """Handle projection change events from the control panel."""
        self.gl.post_resize_event()
