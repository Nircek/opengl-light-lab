from PySide6 import QtWidgets

from opengl_light_lab import AppState, GLWidget


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Edytor efektów świetlnych")
        self.app_state = AppState()
        self.gl = GLWidget(self, self.app_state)
        self.setCentralWidget(self.gl)
        self.resize(1024, 768)
