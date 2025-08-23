import importlib
import logging
import json
import time
import sys
import traceback
from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QWidget, QGridLayout, QMessageBox, \
    QFileDialog
from PySide6.QtCore import Qt

from gui.left_panel import LeftPanel
from gui.right_panel import RightPanel
from gui.bottom_panel import BottomPanel
from viewer.pyside_vtk_viewer import VTKQtViewer
from atlas_runtime import atlas_occ

PROGRAM_NAME = 'Atlas Protocol'
PROGRAM_VERSION = '0.1'


WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 750
PANEL_CONTROL_WIDTH = 300
PANEL_BOM_WIDTH = 300
PANEL_DRAWING_HEIGHT = 200
PANEL_TOP_HEIGHT = 100

APP_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = APP_ROOT / 'models'
MODELS_PKG = 'models'

log = logging.getLogger(__name__)

if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))


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

        self.setWindowTitle(f'{PROGRAM_NAME} v{PROGRAM_VERSION}')
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        central = QWidget()
        self.setCentralWidget(central)

        grid = QGridLayout(central)
        grid.setSpacing(8)

        # Left Panel
        self.left_panel = LeftPanel()
        self.left_panel.setFixedWidth(PANEL_CONTROL_WIDTH)
        self.left_panel.export_btn.setEnabled(False)
        self.left_panel.exportStepRequested.connect(self._export_step)

        self.current_model_name = 'atlas_model'
        self.current_shapes = []

        grid.addWidget(self.left_panel, 0, 0, 1, 1)

        # 3D Viewer Panel (Center)
        self.vtk_panel = VTKQtViewer()
        self.vtk_panel.setMinimumHeight(400)
        self.vtk_panel.setMinimumWidth(600)
        grid.addWidget(self.vtk_panel, 0, 1, 1, 1)

        # Right Panel
        self.right_panel = RightPanel()
        self.right_panel.setFixedWidth(PANEL_BOM_WIDTH)
        self.right_panel.setMinimumWidth(PANEL_BOM_WIDTH)
        grid.addWidget(self.right_panel, 0, 2, 1, 1)

        # Bottom Panel
        self.bottom_panel = BottomPanel()
        self.bottom_panel.setFixedHeight(PANEL_DRAWING_HEIGHT)
        self.bottom_panel.setMinimumHeight(PANEL_DRAWING_HEIGHT)
        grid.addWidget(self.bottom_panel, 1, 0, 1, 3)

        # Stretch settings
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 0)
        grid.setColumnStretch(1, 2)

        # ComboBox
        self._models = {}
        self.left_panel.rescan_btn.clicked.connect(
            self._scan_and_update_models)
        self.left_panel.model_combo.currentIndexChanged.connect(
            self._load_selected_model)

        # Initial scan
        self._scan_and_update_models()

        # Update model options menu
        self.left_panel.regenerateRequested.connect(
            self._regenerate_current_model)
        self._current_mod = None
        self._current_fn_name = None
        self._current_schema = []

    def _scan_and_update_models(self) -> None:
        self._models.clear()
        MODELS_DIR.mkdir(parents=True, exist_ok=True)

        for entry in MODELS_DIR.iterdir():
            if not entry.is_dir():
                continue

            init_path = entry / '__init__.py'
            if not init_path.is_file():
                if entry.name != '__pycache__':
                    log.info(f'Skipping "{entry.name}" - Must be a package')
                continue

            display_name = entry.name
            func_name = 'assembly'

            cfg_path = entry / 'config.json'
            if cfg_path.is_file():
                try:
                    data = json.loads(cfg_path.read_text(encoding='utf-8'))
                    display_name = data.get('name', display_name)
                    func_name = data.get('entry', func_name)
                except Exception as e:
                    log.error(f'[models] Failed reading {cfg_path}: {e}')

            # Build a **package** name, not a path
            mod_qualname = f'{MODELS_PKG}.{entry.name}'
            self._models[display_name] = {
                'module': mod_qualname,
                'folder': entry.name,
                'func': func_name,
            }

        # Populate combo…
        self.left_panel.model_combo.blockSignals(True)
        self.left_panel.model_combo.clear()
        if self._models:
            self.left_panel.model_combo.addItems(sorted(self._models.keys()))
        else:
            logging.info('No models found')
            self.left_panel.model_combo.addItem('No models found')
        self.left_panel.model_combo.blockSignals(False)

        if self._models:
            first = self.left_panel.model_combo.itemText(0)
            self._load_selected_model(first)
            self.left_panel.model_combo.setCurrentIndex(0)

    def _load_selected_model(self, arg: str | int) -> None:
        """
        Import selected model module and render its triangles.
        Update menu with model options.

        """

        if isinstance(arg, int):
            display_name = self.left_panel.model_combo.itemText(arg)
        else:
            display_name = str(arg)

        info = self._models.get(display_name)
        if not info:
            return

        mod_name = info['module']
        func_name = info['func']

        try:
            if mod_name in list(sys.modules.keys()):
                mod = importlib.reload(importlib.import_module(mod_name))
            else:
                mod = importlib.import_module(mod_name)

            if not hasattr(mod, func_name):
                raise AttributeError(
                    f'Module {mod_name} has no function {func_name}')

            # 1) schema -> build controls
            schema = getattr(mod, 'PARAMS', [])
            self.left_panel.build_controls(schema)

            # 2) store current
            self._current_mod = mod
            self._current_fn_name = func_name
            self._current_schema = schema

            # 3) first render using current UI values (defaults)
            fn = getattr(mod, func_name)
            kwargs = self.left_panel.values()
            kwargs = self._coerce_kwargs(kwargs)

            shapes = fn(**kwargs)

            self.current_shapes = shapes
            self.current_model_name = display_name

            if not isinstance(shapes, list) or not shapes:
                log.error(f'[models] Assembly must return list of shapes')
                raise TypeError('assembly() must return list[TopoDS_Shape]')

            compound = atlas_occ.make_compound(shapes)
            tris = atlas_occ.get_triangles(compound)
            self.vtk_panel.load_triangles(tris)
            self.left_panel.export_btn.setEnabled(True)

        except Exception as e:
            log.error(f'[models] Failed to load {display_name}: {e}')
            traceback.print_exc()

    def _regenerate_current_model(self) -> None:
        if not self._current_mod or not self._current_fn_name:
            return
        try:
            fn = getattr(self._current_mod, self._current_fn_name)
            kwargs = self.left_panel.values()
            kwargs = self._coerce_kwargs(kwargs)

            shapes = fn(**kwargs)
            self.current_shapes = shapes

            if not isinstance(shapes, list) or not shapes:
                raise TypeError('assembly() must return list[TopoDS_Shape]')

            compound = atlas_occ.make_compound(shapes)
            tris = atlas_occ.get_triangles(compound)
            self.vtk_panel.load_triangles(tris)
        except Exception as e:
            log.error(f'[models] Failed to regenerate current model: {e}')
            traceback.print_exc()

    def _coerce_kwargs(self, kwargs: dict) -> dict:
        out = dict(kwargs)

        def _tname(tn):
            if tn in (float, int, bool, str):
                return {
                    float: 'float', int: 'int', bool: 'bool', str: 'str'}[tn]
            if isinstance(tn, str):
                return tn.lower()
            return 'str'

        for p in self._current_schema or []:
            name = p['name']
            t = _tname(p.get('type', 'float'))
            if name not in out:
                continue
            v = out[name]
            try:
                if t == 'float':
                    out[name] = float(v)
                elif t == 'int':
                    out[name] = int(v)
                elif t == 'bool':
                    out[name] = v if isinstance(v, bool) else str(
                        v).lower() in ('1', 'true', 'yes', 'on')
            except Exception as e:
                log.error(
                    f'[models] Failed to coerce "{name}" ({v!r}) to {t}: {e}')
        return out

    def _export_step(self) -> None:
        """ Codename: BloatyMcStepFile and the BaggageReclaimer """
        shapes = getattr(self, 'current_shapes', None)
        if not shapes:
            QMessageBox.information(self, 'Export', 'Nothing to export.')
            return

        # Estimate size and confirm
        n = len(shapes)
        est_bytes = n * 19_500  # Size estimation based upon simple box shape
        est_gb = est_bytes / (1024 ** 3)
        HARD_CAP = 50_000 # TODO: Move to config file.

        if n >= HARD_CAP:
            reply = QMessageBox.question(
                self, 'Huge export',
                f'This will export ~{n:,} solids.\n'
                f'Estimated STEP size ≈ {est_gb:.2f} GB.\n\nProceed?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                logging.info(
                    f'Export cancelled at {n:,} solids (est {est_gb:.2f} GB).')
                return
            logging.info(
                f'Absolute madman, exporting: {n:,} solids '
                f'(est {est_gb:.2f} GB).')

        suggested = f"{getattr(self, 'current_model_name', 'atlas_model')}.step"
        start = str(Path.home() / suggested)
        path, _ = QFileDialog.getSaveFileName(
            self, 'Export STEP', start, 'STEP (*.step *.stp)')
        if not path:
            return

        p = Path(path)
        if p.suffix.lower() not in ('.step', '.stp'):
            p = p.with_suffix('.step')
        path = str(p)

        try:
            self.left_panel.export_btn.setEnabled(False)
            t0 = time.perf_counter()
            self.setCursor(Qt.CursorShape.BusyCursor)
            compound = atlas_occ.make_compound(shapes)
            atlas_occ.export_step(compound, path)
            dt = time.perf_counter() - t0
            QMessageBox.information(self, 'Export', f'Exported:\n{path}')
            logging.info(f'Export finished in {dt:.2f}s -> {path}')
        except Exception as e:
            logging.critical(f'[models] Failed to export STEP: {e}')
            QMessageBox.critical(self, 'Export failed', str(e))
        finally:
            self.unsetCursor()
            self.left_panel.export_btn.setEnabled(True)
