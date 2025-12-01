"""Entry point for the OpenGL Light Lab application."""

import sys

from PySide6 import QtWidgets

from opengl_light_lab import MainWindow


def main() -> None:
    """Run the application."""
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
