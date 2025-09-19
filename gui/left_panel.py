from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, \
    QComboBox, QFormLayout, QSpinBox, QDoubleSpinBox, QCheckBox, QLineEdit, \
    QScrollArea, QFrame
from PySide6.QtCore import Signal, QTimer
from PySide6 import QtCore


class LeftPanel(QWidget):
    regenerateRequested = Signal()
    exportStepRequested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName('Panel')
        # noinspection PyUnresolvedReferences
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        self.model_combo = QComboBox()
        self.rescan_btn = QPushButton('↻ Rescan Models')
        self.export_btn = QPushButton('⬇ Export STEP')

        # --- Static header (never cleared) ---
        root = QVBoxLayout(self)
        self.setLayout(root)
        root.addWidget(QLabel("Controls"))
        root.addWidget(self.model_combo)
        root.addWidget(self.rescan_btn)
        root.addWidget(self.export_btn)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        root.addWidget(self.scroll, 1)
        root.addStretch(0)

        # Model options container
        self._controls_host = QFrame()
        self._form = QFormLayout(self._controls_host)
        self._form.setContentsMargins(6, 6, 6, 6)
        self._form.setSpacing(8)
        self.scroll.setWidget(self._controls_host)

        self._editors = {}
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(150)
        self._debounce.timeout.connect(self.regenerateRequested)
        self.export_btn.clicked.connect(self.exportStepRequested.emit)

    def build_controls(self, schema: list[dict]) -> None:
        # Clear dynamic controls only (not header)
        for i in reversed(range(self._form.count())):
            w = self._form.itemAt(i).widget()
            if w:
                w.setParent(None)
        self._editors.clear()

        for p in schema or []:
            t = p.get("type", "float")
            name = p["name"]
            label = p.get("label", name)
            default = p.get("default")

            if t == "float":
                w = QDoubleSpinBox()
                w.setRange(p.get("min", -1e9), p.get("max", 1e9))
                w.setSingleStep(p.get("step", 1.0))
                w.setValue(float(default or 0.0))
                w.editingFinished.connect(self.regenerateRequested.emit)
            elif t == "int":
                w = QSpinBox()
                w.setRange(int(p.get("min", -10 ** 9)),
                           int(p.get("max", 10 ** 9)))
                w.setSingleStep(int(p.get("step", 1)))
                w.setValue(int(default or 0))
                w.editingFinished.connect(self.regenerateRequested.emit)
            elif t == "bool":
                w = QCheckBox()
                w.setChecked(bool(default))
                w.stateChanged.connect(self.regenerateRequested.emit)
            elif t == "enum":
                from PySide6.QtWidgets import QComboBox
                w = QComboBox()
                for c in p.get("choices", []):
                    w.addItem(str(c))
                if default is not None:
                    w.setCurrentText(str(default))
                w.currentTextChanged.connect(
                    lambda *_: self.regenerateRequested.emit())
            else:
                w = QLineEdit()
                w.setText("" if default is None else str(default))
                w.editingFinished.connect(self.regenerateRequested.emit)

            self._editors[name] = w
            self._form.addRow(label, w)

        if not schema:
            ph = QLabel("No parameters for this model.")
            ph.setStyleSheet("color:#888;")
            self._form.addRow(ph)

    def values(self) -> dict:
        from PySide6.QtWidgets import QDoubleSpinBox, QSpinBox, QCheckBox, \
            QComboBox, QLineEdit
        vals = {}
        for name, w in self._editors.items():
            if isinstance(w, QDoubleSpinBox):
                vals[name] = float(w.value())
            elif isinstance(w, QSpinBox):
                vals[name] = int(w.value())
            elif isinstance(w, QCheckBox):
                vals[name] = bool(w.isChecked())
            elif isinstance(w, QComboBox):
                vals[name] = w.currentText()
            elif isinstance(w, QLineEdit):
                vals[name] = w.text()
        return vals

    def cancel_pending_regen(self) -> None:
        self._debounce.stop()
