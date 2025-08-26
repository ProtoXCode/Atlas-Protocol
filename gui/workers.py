from __future__ import annotations
import time, traceback, sys
import logging

from PySide6.QtCore import QObject, Signal, QRunnable

from atlas_runtime.asm_utils import normalize_assembly, \
    build_compound_and_triangles


class WorkerSignals(QObject):
    result = Signal(object, dict)  # (asm, stats)
    error = Signal(str)
    finished = Signal()
    progress = Signal(object)


class ModelRunnable(QRunnable):
    def __init__(self, fn, kwargs: dict) -> None:
        super().__init__()
        self.fn = fn
        self.kwargs = kwargs
        self.signals = WorkerSignals()

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

    def run(self) -> None:
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

            try:
                t_inst = self._count_solid_instances(asm.root)
            except Exception as e:
                logging.exception(f'[perf] instance count failed: {e}')
                t_inst = 0

            stats = {
                't_model': t_model,
                't_norm': t_norm,
                't_cache': t_cache,
                't_inst': t_inst,
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


class ExportSignals(QObject):
    finished = Signal(float, str)  # dt, out_path
    error = Signal(str)
    progress = Signal()


class ExportWorker(QRunnable):
    def __init__(self, atlas_occ, compound, path: str) -> None:
        super().__init__()
        self.atlas_occ = atlas_occ
        self.compound = compound
        self.path = path
        self.signals = ExportSignals()

    def run(self) -> None:
        import time, traceback
        try:
            t0 = time.perf_counter()
            self.atlas_occ.export_step(self.compound, self.path)
            dt = time.perf_counter() - t0
            self.signals.finished.emit(dt, self.path)
        except Exception as e:
            traceback.print_exc()
            self.signals.error.emit(str(e))
