from PySide6 import QtCore, QtGui, QtWidgets

from opengl_light_lab import AppState, ControlPanel, GLWidget


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Edytor efektów świetlnych")
        self.app_state = AppState()
        self.gl = GLWidget(self, self.app_state)
        self.gl.makeCurrent()
        self.setCentralWidget(self.gl)

        self.control_panel = ControlPanel(self, self.app_state)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.control_panel)

        self.resize(1280, 768)

    def on_projection_changed(self) -> None:
        app_instance = QtCore.QCoreApplication.instance()
        if app_instance is None:
            print("No QCoreApplication instance found")
            return
        app_instance.postEvent(self.gl, QtGui.QResizeEvent(size := self.gl.size(), size))
