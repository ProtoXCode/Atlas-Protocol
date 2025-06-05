from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox)


class LeftPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Controls"))
        layout.addWidget(QComboBox())  # Placeholder for model dropdown
        layout.addWidget(QPushButton("↻ Rescan Models"))
        layout.addStretch()
