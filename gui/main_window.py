import importlib
import logging
import json
import sys
import os
import time
from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QWidget, QGridLayout, QMessageBox, \
    QFileDialog, QApplication
from PySide6.QtCore import Qt, QThreadPool, QTimer

from atlas_runtime import build_compound_and_triangles
from gui.left_panel import LeftPanel
from gui.right_panel import RightPanel
from gui.bottom_panel import BottomPanel
from gui.workers import ModelRunnable, ExportWorker
from viewer.pyside_vtk_viewer import VTKQtViewer

PROGRAM_NAME = 'Atlas Protocol'
PROGRAM_VERSION = '0.2'

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

        self.pool = QThreadPool.globalInstance()
        self.pool.setMaxThreadCount(max(2, os.cpu_count() - 2))
        self._job_running = False
        self._pending_job = None

        grid = QGridLayout(central)
        grid.setSpacing(8)

        # --- Panels ---
        self.left_panel = LeftPanel()
        self.left_panel.setFixedWidth(PANEL_CONTROL_WIDTH)
        self.left_panel.export_btn.setEnabled(False)

        self.vtk_panel = VTKQtViewer()
        self.vtk_panel.setMinimumHeight(400)
        self.vtk_panel.setMinimumWidth(600)

        self.right_panel = RightPanel()
        self.right_panel.setFixedWidth(PANEL_BOM_WIDTH)
        self.right_panel.setMinimumWidth(PANEL_BOM_WIDTH)

        self.bottom_panel = BottomPanel()
        self.bottom_panel.setFixedHeight(PANEL_DRAWING_HEIGHT)
        self.bottom_panel.setMinimumHeight(PANEL_DRAWING_HEIGHT)

        grid.addWidget(self.left_panel, 0, 0, 1, 1)
        grid.addWidget(self.vtk_panel, 0, 1, 1, 1)
        grid.addWidget(self.right_panel, 0, 2, 1, 1)
        grid.addWidget(self.bottom_panel, 1, 0, 1, 3)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 0)
        grid.setColumnStretch(1, 2)

        self._models = {}
        self._current_mod = None
        self._current_fn_name = None
        self._current_schema = []
        self.current_model_name = 'atlas_model'
        self.current_assembly = None
        self._busy = False

        self.left_panel.exportStepRequested.connect(self._export_step_async)
        self.left_panel.regenerateRequested.connect(
            self._regenerate_current_model)
        self.left_panel.rescan_btn.clicked.connect(
            self._scan_and_update_models)
        self.left_panel.model_combo.currentIndexChanged.connect(
            self._load_selected_model)

        QTimer.singleShot(0, self._scan_and_update_models)

    @staticmethod
    def _count_solid_instances(inst) -> int:
        """ Sum quantity of all nodes that actually have a shape in model. """
        total = 0
        stack = [(inst, 1)]
        while stack:
            node, parent_qty = stack.pop()
            qty = parent_qty * int(getattr(node, 'qty', 1))
            if getattr(getattr(node, 'ref', None), 'shape', None) is not None:
                total += qty
            for ch in getattr(node, 'children', []) or []:
                stack.append((ch, qty))
        return total

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
                'func': func_name}

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
            self.left_panel.model_combo.blockSignals(True)
            self.left_panel.model_combo.setCurrentIndex(0)
            self.left_panel.model_combo.blockSignals(False)
            self._load_selected_model(first)

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

            # 3) first render using current UI values (defaults) via the pipeline
            fn = getattr(mod, func_name)
            kwargs = self._coerce_kwargs(self.left_panel.values())

            self._start_model_job(fn, kwargs, display_name)

        except Exception as e:
            logging.exception(f'[models] Failed to load {display_name}: {e}')

    def _regenerate_current_model(self) -> None:
        if self._job_running:
            logging.info('[regen] Suppressed during busy operation')
            return

        if not self._current_mod or not self._current_fn_name:
            return

        try:
            fn = getattr(self._current_mod, self._current_fn_name)
            kwargs = self._coerce_kwargs(self.left_panel.values())

            self._start_model_job(fn, kwargs)


        except Exception as e:
            logging.exception(
                f'[models] Failed to regenerate current model: {e}')

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

    def _start_model_job(
            self, fn, kwargs: dict, display_name: str | None = None) -> None:

        if self._job_running:
            self._pending_job = (fn, kwargs, display_name)
            logging.info('[model] queued pending job')
            return

        self._job_running = True
        self.left_panel.export_btn.setEnabled(False)

        self.setCursor(Qt.CursorShape.WaitCursor)

        job = ModelRunnable(fn, kwargs)
        self._last_job = job

        def _on_result(processed_data, stats):
            try:
                self.unsetCursor()

                asm = processed_data['assembly']
                optimized_triangles = processed_data['triangles']

                logging.info(
                    f'[main] Loading pre-processed triangles into VTK...')
                vtk_start = time.perf_counter()

                self.vtk_panel.load_triangles(optimized_triangles)

                vtk_time = time.perf_counter() - vtk_start
                logging.info(f'[main] VTK load time: {vtk_time:.3f}s')

                self.current_assembly = asm
                if display_name:
                    self.current_model_name = display_name

                # Update BOM
                if hasattr(self.right_panel, 'set_bom'):
                    QTimer.singleShot(10, lambda: self._update_bom(asm))

                # Log performance and stats
                logging.info(
                    f"[perf] optimized pipeline{f' ({display_name})' if display_name else ''} "
                    f"model={stats['t_model']:.3f}s norm={stats['t_norm']:.3f}s "
                    f"cache={stats['t_cache']:.3f}s prep={stats['t_vtk_prep']:.3f}s "
                    f"vtk={vtk_time:.3f}s total={stats['t_total']:.3f}s "
                    f"inst={stats['t_inst']:,} tris={stats['tris']:,}")

                self.left_panel.export_btn.setEnabled(True)
                self._show_perf_in_status(stats, vtk_time, display_name)

            except Exception as e:
                self.unsetCursor()
                logging.exception(f'[model] result handler failed: {e}')

        def _on_error(msg: str) -> None:
            try:
                self.unsetCursor()
                logging.exception(f'[model] failed: {msg}')
                QMessageBox.critical(self, 'Model failed', msg)
                self.left_panel.export_btn.setEnabled(True)

            except Exception as e:
                logging.exception(f'[model] error handler failed: {e}')

        def _on_finished() -> None:
            try:
                self.unsetCursor()
                self._job_running = False
                if self._pending_job:
                    fn2, kw2, name2 = self._pending_job
                    self._pending_job = None
                    QTimer.singleShot(
                        0, lambda: self._start_model_job(fn2, kw2, name2))

            except Exception as e:
                logging.exception(f'[model] finished handler failed: {e}')
                self._job_running = False

        def _on_progress(msg: str) -> None:
            try:
                self.statusBar().showMessage(msg)
            except Exception as e:
                logging.exception(f'[model] progress handler failed: {e}')

        # Connect signals
        job.signals.result.connect(
            _on_result, Qt.ConnectionType.QueuedConnection)
        job.signals.error.connect(
            _on_error, Qt.ConnectionType.QueuedConnection)
        job.signals.finished.connect(
            _on_finished, Qt.ConnectionType.QueuedConnection)
        job.signals.progress.connect(
            _on_progress, Qt.ConnectionType.QueuedConnection)

        # Start the job
        self.pool.start(job)

    def _update_bom(self, asm):
        """
        Update BOM in a separate method to avoid blocking main result handler
        """
        try:
            from atlas_runtime.asm_utils import bom_flat, bom_rollup
            bom_start = time.perf_counter()
            self.right_panel.set_bom(bom_rollup(bom_flat(asm)))
            bom_time = time.perf_counter() - bom_start
            logging.info(f'[main] BOM update took {bom_time:.3f}s')
        except Exception as e:
            logging.exception(f'[model] BOM update failed: {e}')

    def _export_step_async(self) -> None:
        """ Async version of STEP export using worker thread """
        self.left_panel.cancel_pending_regen()
        if getattr(self, '_busy', False):
            logging.info('[export] blocked: busy flag set')
            return

        asm = getattr(self, 'current_assembly', None)
        if not asm or asm.compound is None:
            QMessageBox.information(self, 'Export', 'Nothing to export.')
            return

        # Get file path first (on main thread)
        suggested = f'{getattr(self, 'current_model_name', 'atlas_model')}.step'
        start = str(Path.home() / suggested)
        path, _ = QFileDialog.getSaveFileName(
            self, 'Export STEP', start, 'STEP (*.step *.stp)'
        )
        if not path:
            return

        p = Path(path)
        if p.suffix.lower() not in ('.step', '.stp'):
            p = p.with_suffix('.step')
        path = str(p)

        # Estimate size and warn if needed
        try:
            n = self._count_solid_instances(asm.root)
            est_bytes = n * 19_500
            est_gb = est_bytes / (1024 ** 3)
            HARD_CAP = 50_000
            if n >= HARD_CAP:
                reply = QMessageBox.question(
                    self,
                    'Huge export',
                    f'This will export ~{n:,} solids.\n'
                    f'Estimated STEP size ~{est_gb:.2f} GB.\n\nProceed?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    logging.info(
                        f'[export] canceled at {n:,} solids (~{est_gb:.2f} GB)')
                    return

        except Exception as e:
            logging.exception(f'[export] size estimation failed: {e}')

        # Start async export
        self._busy = True
        self.left_panel.export_btn.setEnabled(False)
        self.setCursor(Qt.CursorShape.WaitCursor)

        # Import atlas_occ here to avoid any import issues
        from atlas_runtime import atlas_occ

        export_worker = ExportWorker(atlas_occ, asm.compound, path)

        def _on_export_finished(dt: float, out_path: str) -> None:
            try:
                self.unsetCursor()
                QMessageBox.information(self, 'Export',
                                        f'Exported:\n{out_path}')
                logging.info(f'[export] finished in {dt:.2f}s -> {out_path}')

            except Exception as e:
                logging.exception(f'[export] finish handler failed: {e}')

            finally:
                self.left_panel.export_btn.setEnabled(True)
                self._busy = False

        def _on_export_error(msg: str) -> None:
            try:
                self.unsetCursor()
                logging.exception(f'[export] failed: {msg}')
                QMessageBox.critical(self, 'Export failed', msg)

            except Exception as e:
                logging.exception(f'[export] error handler failed: {e}')

            finally:
                self.left_panel.export_btn.setEnabled(True)
                self._busy = False

        def _on_export_progress(msg: str) -> None:
            try:
                self.statusBar().showMessage(msg)

            except Exception as e:
                logging.exception(f'[export] progress handler failed: {e}')

        # Connect signals
        export_worker.signals.finished.connect(
            _on_export_finished, Qt.ConnectionType.QueuedConnection)
        export_worker.signals.error.connect(
            _on_export_error, Qt.ConnectionType.QueuedConnection)
        export_worker.signals.progress.connect(
            _on_export_progress, Qt.ConnectionType.QueuedConnection)

        # Start export
        self.pool.start(export_worker)

    def _process_assembly_chunked(self, asm, stats, display_name=None):
        """ Process assembly in chunks with GUI updates between """

        # Show progress
        self.setCursor(Qt.CursorShape.WaitCursor)
        self.statusBar().showMessage('Building geometry...')

        # Step 1: Build triangles with periodic GUI updates
        self._chunk_build_triangles(asm, stats, display_name)

    def _chunk_build_triangles(self, asm, stats, display_name):
        """ Build triangles with chunked processing """
        self._current_asm = asm
        self._current_stats = stats
        self._current_display_name = display_name

        start_time = time.perf_counter()

        # Try to build triangles in one go, but with processEvents
        try:
            # Process events every 100ms during triangle building
            self._triangle_timer = QTimer()
            self._triangle_timer.timeout.connect(
                self._process_events_during_triangles)
            self._triangle_timer.start(50)  # Process events every 50ms

            # Do the heavy lifting
            build_compound_and_triangles(asm)

            # Stop the timer
            self._triangle_timer.stop()

            cache_time = time.perf_counter() - start_time
            stats['t_cache'] = cache_time

            # Continue with VTK processing
            self._chunk_vtk_processing()

        except Exception as e:
            if hasattr(self, '_triangle_timer'):
                self._triangle_timer.stop()
            raise e

    @staticmethod
    def _process_events_during_triangles():
        """ Process GUI events during triangle building """
        QApplication.processEvents()

    def _chunk_vtk_processing(self):
        """ Process VTK loading in chunks """
        asm = self._current_asm
        stats = self._current_stats
        display_name = self._current_display_name

        if not asm.triangles:
            raise TypeError('Model produced no triangles')

        # Count instances
        try:
            stats['t_inst'] = self._count_solid_instances(asm.root)
        except Exception as e:
            logging.exception(f'[perf] instance count failed: {e}')
            stats['t_inst'] = 0

        stats['tris'] = len(asm.triangles or [])

        # If we have a lot of triangles, process VTK in chunks
        if len(asm.triangles) > 10000:
            self._chunk_vtk_large(asm, stats, display_name)
        else:
            self._process_vtk_simple(asm, stats, display_name)

    def _chunk_vtk_large(self, asm, stats, display_name):
        """ Handle large triangle counts with chunked VTK processing """
        self.statusBar().showMessage(
            f'Loading {len(asm.triangles):,} triangles...')

        # Create a timer to process VTK with GUI updates
        self._vtk_timer = QTimer()
        self._vtk_start_time = time.perf_counter()

        # Start VTK processing on next event loop iteration
        QTimer.singleShot(10, lambda: self._do_vtk_with_progress(asm, stats,
                                                                 display_name))

    def _do_vtk_with_progress(self, asm, stats, display_name):
        """ Do VTK processing with periodic progress updates """
        try:
            # Process events before starting
            QApplication.processEvents()

            vtk_start = time.perf_counter()

            # Use the optimized VTK loader
            self._load_triangles_optimized(asm.triangles)

            vtk_time = time.perf_counter() - vtk_start
            logging.info(f'[main] VTK loading took {vtk_time:.3f}s')

            # Finish up
            self._finish_model_processing(asm, stats, display_name, vtk_time)

        except Exception as e:
            logging.exception(f'[model] VTK processing failed: {e}')

    def _load_triangles_optimized(self, triangles):
        """Optimized triangle loading with progress updates"""
        triangle_count = len(triangles)

        if triangle_count < 1000:
            self.vtk_panel.load_triangles(triangles)
            return

        logging.info(
            f'[vtk] Loading {triangle_count:,} triangles with optimization')

        # Update status periodically during VTK operations
        original_render_mesh = self.vtk_panel.render_mesh

        def render_mesh_with_progress(tris):
            # Process events every so often during mesh building
            for i in range(0, len(tris), 10000):
                if i > 0:
                    self.statusBar().showMessage(
                        f'Processing triangles {i:,}/{len(tris):,}...')
                    QApplication.processEvents()
            return original_render_mesh(tris)

        # Temporarily replace the render_mesh method
        self.vtk_panel.render_mesh = render_mesh_with_progress

        try:
            self.vtk_panel.load_triangles(triangles)
        finally:
            # Restore original method
            self.vtk_panel.render_mesh = original_render_mesh

    def _process_vtk_simple(self, asm, stats, display_name):
        """Simple VTK processing for small models"""
        vtk_start = time.perf_counter()
        self.vtk_panel.load_triangles(asm.triangles)
        vtk_time = time.perf_counter() - vtk_start
        logging.info(f'[main] VTK loading took {vtk_time:.3f}s')

        self._finish_model_processing(asm, stats, display_name, vtk_time)

    def _finish_model_processing(self, asm, stats, display_name,
                                 vtk_time: float = 0.0) -> None:
        """ Finish model processing and update UI """
        try:
            self.current_assembly = asm
            if display_name:
                self.current_model_name = display_name

            # Update BOM
            if hasattr(self.right_panel, 'set_bom'):
                try:
                    from atlas_runtime.asm_utils import bom_flat, bom_rollup
                    self.right_panel.set_bom(bom_rollup(bom_flat(asm)))
                except Exception as e:
                    logging.exception(f'[model] set_bom failed: {e}')

            # Log performance
            logging.info(
                f"[perf] chunked pipeline{f' ({display_name})' if display_name else ''} "
                f"model={stats['t_model']:.3f}s norm={stats['t_norm']:.3f}s "
                f"cache={stats['t_cache']:.3f}s total={stats['t_total']:.3f}s "
                f"inst={stats['t_inst']:,} tris={stats['tris']:,}")

            self._show_perf_in_status(stats, vtk_time, display_name)

            # Clean up
            self.unsetCursor()
            self.statusBar().clearMessage()
            self.left_panel.export_btn.setEnabled(True)

        except Exception as e:
            self.unsetCursor()
            logging.exception(f'[model] finish processing failed: {e}')

    def _show_perf_in_status(self, stats: dict, vtk_time: float,
                             display_name: str | None = None) -> None:
        # Build a compact single-line status with thousands separators
        name = f' ({display_name})' if display_name else ''
        msg = (
            f'Pipeline{name} | '
            f'model={stats['t_model']:.3f}s  norm={stats['t_norm']:.3f}s  '
            f'cache={stats['t_cache']:.3f}s  prep={stats.get('t_vtk_prep', 0.0):.3f}s  '
            f'vtk={vtk_time:.3f}s  total={stats['t_total']:.3f}s  '
            f'inst={stats.get('t_inst', 0):,}  tris={stats.get('tris', 0):,}'
        )
        try:
            self.statusBar().showMessage(msg)
        except Exception as e:
            logging.exception(f'[ui] failed updating status bar: {e}')
