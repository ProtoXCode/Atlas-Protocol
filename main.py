from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
import sys
import qt_material

if __name__ == "__main__":
    app = QApplication(sys.argv)

    qt_material.apply_stylesheet(app, theme='dark_blue.xml')

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
