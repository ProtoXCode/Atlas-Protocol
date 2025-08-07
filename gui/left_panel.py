from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, \
    QComboBox
from PySide6 import QtCore


class LeftPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('Panel')
        # noinspection PyUnresolvedReferences
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        layout.addWidget(QLabel('Controls'))

        self.model_combo = QComboBox()
        self.rescan_btn = QPushButton('↻ Rescan Models')


        layout.addWidget(self.model_combo)
        layout.addWidget(self.rescan_btn)
        layout.addStretch()
