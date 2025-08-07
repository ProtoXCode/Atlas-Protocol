from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6 import QtCore

class BottomPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('Panel')
        # noinspection PyUnresolvedReferences
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.addWidget(QLabel('Drawing / Export Previews'))
        layout.addStretch()
