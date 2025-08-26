from __future__ import annotations
import time, traceback, sys
import logging

from PySide6.QtCore import QObject, Signal, Slot, QRunnable

from atlas_runtime.asm_utils import normalize_assembly, \
    build_compound_and_triangles


class WorkerSignals(QObject):
    result = Signal(object, dict)
    error = Signal(str)
    finished = Signal()


class ModelRunnable(QRunnable):
    def __init__(self, fn, kwargs: dict):
        super().__init__()
        self.fn = fn
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            t_all = time.perf_counter()

            t0 = time.perf_counter()
            result = self.fn(**self.kwargs)
            t_model = time.perf_counter() - t0

            t1 = time.perf_counter()
            asm = normalize_assembly(result)
            t_norm = time.perf_counter() - t1

            t2 = time.perf_counter()
            build_compound_and_triangles(asm)
            t_cache = time.perf_counter() - t2

            stats = {
                't_model': t_model,
                't_norm': t_norm,
                't_cache': t_cache,
                't_total': time.perf_counter() - t_all,
                'tris': len(asm.triangles or []),
            }
            self.signals.result.emit(asm, stats)
        except Exception as e:
            self.signals.error.emit(traceback.format_exc())
            logging.error(f'Workers pool exception: {e}')
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit(f'{exctype.__name__}: {value}')
        finally:
            self.signals.finished.emit()


class ExportWorker(QRunnable):
    finished = Signal(float, str)
    error = Signal(str)

    def __init__(self, atlas_occ, compound, path: str) -> None:
        super().__init__()
        self.atlas_occ = atlas_occ
        self.compound = compound
        self.path = path

    @Slot()
    def run(self) -> None:
        import time
        try:
            t0 = time.perf_counter()
            self.atlas_occ.export_step(self.compound, self.path)
            dt = time.perf_counter() - t0
            self.finished.emit(dt, self.path)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))
