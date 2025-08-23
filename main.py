#!/usr/bin/env python3
import sys
import os
from pathlib import Path

from PySide6.QtGui import QIcon

from atlas.logging_setup import configure_logging

configure_logging()

ICON_PATH = Path(__file__).resolve().parent / 'assets/icons/protox.png'

# --- force Qt to use X11 when running on Wayland, works on Fedora ---
if os.name == 'posix':
    if os.environ.get('XDG_SESSION_TYPE', '').lower() == 'wayland':
        os.environ.setdefault('QT_QPA_PLATFORM', 'xcb')

from PySide6.QtWidgets import QApplication
import qt_material

from gui.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(ICON_PATH)))
    qt_material.apply_stylesheet(app, theme='dark_blue.xml')

    # Load theme
    with open('gui/theme.qss', 'r', encoding='utf-8') as f:
        app.setStyleSheet(app.styleSheet() + '\n' + f.read())

    window = MainWindow()
    window.setWindowIcon(QIcon(str(ICON_PATH)))
    window.show()
    sys.exit(app.exec())
