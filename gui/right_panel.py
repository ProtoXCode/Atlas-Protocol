from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6 import QtCore

class RightPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('Panel')
        # noinspection PyUnresolvedReferences
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('BOM / Details'))
        layout.addStretch()

    def set_bom(self, bom) -> None:
        pass # TODO: Implement
