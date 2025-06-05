from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout)
from gui.left_panel import LeftPanel
from gui.right_panel import RightPanel
from gui.bottom_panel import BottomPanel
from viewer.pyside_vtk_viewer import VTKQtViewer

PROGRAM_NAME = 'Atlas Protocol'
PROGRAM_VERSION = 'v0.1'

WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 750
PANEL_CONTROL_WIDTH = 300
PANEL_BOM_WIDTH = 300
PANEL_DRAWING_HEIGHT = 200
PANEL_TOP_HEIGHT = 100
MODELS_DIR = './models'


class MainWindow(QMainWindow):
    """
    Main GUI application window for the Atlas Protocol system.
    This window serves as the central hub for logic-driven mechanical
    resolution, including UI panels for:
         - Parameterized input and control (left)
         - Real-time 3D model viewer (center)
         - Resolved BOM overview (right)
        - Drawing/export previews (bottom)

    Designed as a logic-first interface for interacting with declarative part
    definitions, structure resolution, and digital twin output.

    Layout is modular, grid-based, and scalable for future extensions like:
        - Module selection dropdowns
        - CSV input triggers
        - Viewer → Code navigation
        - Export and ERP linkage

    This class defines the UI shell. Functional logic is executed via embedded
    modules.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Atlas Protocol PySide6 MVP")
        self.resize(1500, 750)
        central = QWidget()
        self.setCentralWidget(central)

        grid = QGridLayout(central)
        grid.setSpacing(8)

        # Left Panel
        self.left_panel = LeftPanel()
        self.left_panel.setFixedWidth(PANEL_CONTROL_WIDTH)
        self.left_panel.setMinimumWidth(PANEL_CONTROL_WIDTH)
        grid.addWidget(self.left_panel, 0, 0, 2, 1)

        # 3D Viewer Panel (Center)
        self.vtk_panel = VTKQtViewer("models/atlas_test_cube/cube.stl")
        self.vtk_panel.setMinimumHeight(400)
        self.vtk_panel.setMinimumWidth(600)
        grid.addWidget(self.vtk_panel, 0, 1, 1, 1)

        # Right Panel
        self.right_panel = RightPanel()
        self.right_panel.setFixedWidth(PANEL_BOM_WIDTH)
        self.right_panel.setMinimumWidth(PANEL_BOM_WIDTH)
        grid.addWidget(self.right_panel, 0, 2, 2, 1)

        # Bottom Panel
        self.bottom_panel = BottomPanel()
        self.bottom_panel.setFixedHeight(PANEL_DRAWING_HEIGHT)
        self.bottom_panel.setMinimumHeight(PANEL_DRAWING_HEIGHT)
        grid.addWidget(self.bottom_panel, 1, 0, 1, 3)

        # Stretch settings
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 0)
        grid.setColumnStretch(1, 2)
