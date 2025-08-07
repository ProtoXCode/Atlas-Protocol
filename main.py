import sys

from PySide6.QtWidgets import QApplication
import qt_material

from gui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qt_material.apply_stylesheet(app, theme='dark_blue.xml')

    # Load theme
    with open('gui/theme.qss', 'r', encoding='utf-8') as f:
        app.setStyleSheet(app.styleSheet() + '\n' + f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
