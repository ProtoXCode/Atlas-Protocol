from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel


class BottomPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.addWidget(QLabel("Drawing / Export Previews"))
        layout.addStretch()
